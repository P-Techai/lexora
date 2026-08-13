from datetime import datetime, timezone
import hashlib
import time
import urllib.request
import urllib.parse
from typing import List, Optional

from src.application.dto.acquisition_dto import AcquisitionRequest, AcquisitionResult
from src.application.ports.acquisition_provider import DocumentAcquisitionProvider
from src.application.services.source_registry import SourceRegistryService
from src.domain.entities.acquisition_audit_log import AcquisitionAuditLog
from src.domain.entities.raw_artifact import RawArtifact
from src.domain.entities.source import Source
from src.domain.enums import ChangeStatus
from src.domain.exceptions import (
    AcquisitionFailedError,
    AcquisitionTimeoutError,
    ArtifactTooLargeError,
    RedirectNotAllowedError,
    SSRFProtectionError,
    UnsupportedContentTypeError,
)


class SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Handler urllib customizado para capturar redirect_chain e impedir HTTPS->HTTP downgrade e SSRF."""

    def __init__(self, source_registry: SourceRegistryService, source: Source, redirect_chain: List[str]):
        super().__init__()
        self.source_registry = source_registry
        self.source = source
        self.redirect_chain = redirect_chain

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # 1. Impede estouro de limite de redirects (máximo 5 redirects)
        if len(self.redirect_chain) >= 5:
            raise RedirectNotAllowedError(f"Limite máximo de 5 redirecionamentos HTTP excedido para URL '{newurl}'.")

        # 2. Impede downgrade inseguro de HTTPS para HTTP
        old_url = req.full_url
        if old_url.startswith("https://") and newurl.startswith("http://"):
            raise RedirectNotAllowedError(f"Downgrade inseguro de HTTPS para HTTP proibido para '{newurl}'.")

        # 3. Re-validação SSRF e Governança na nova URL
        valid, warnings = self.source_registry.validate_acquisition_url(self.source, newurl)
        if not valid:
            raise SSRFProtectionError(f"Redirecionamento HTTP SSRF bloqueado para '{newurl}': {warnings}")

        self.redirect_chain.append(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class HttpDocumentAcquisitionAdapter(DocumentAcquisitionProvider):
    """Adaptador de aquisição HTTP real implementando a porta unificada DocumentAcquisitionProvider."""

    def __init__(self, source_registry: SourceRegistryService, allowed_mimes: Optional[List[str]] = None):
        self.source_registry = source_registry
        self.allowed_mimes = allowed_mimes or ["text/html", "text/plain", "application/pdf", "application/xhtml+xml", "application/xml"]
        self._last_request_time = 0.0

    async def acquire(self, request: AcquisitionRequest) -> AcquisitionResult:
        source = request.source
        target_url = request.target_url

        # 1. Validação SSRF e Governança na URL de Entrada
        url_valid, url_warnings = self.source_registry.validate_acquisition_url(source, target_url)
        if not url_valid:
            raise SSRFProtectionError(f"Segurança SSRF: URL '{target_url}' rejeitada para fonte '{source.name}': {url_warnings}")

        # 2. Rate Limiting Polido (máximo 2 requisições/segundo por adaptador)
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < 0.5:
            time.sleep(0.5 - elapsed)
        self._last_request_time = time.time()

        # 3. Safe Redirect Handler
        redirect_chain: List[str] = [target_url]
        redirect_handler = SafeRedirectHandler(self.source_registry, source, redirect_chain)
        opener = urllib.request.build_opener(redirect_handler)

        req_headers = {
            "User-Agent": "LEXORA-Bot/1.0 (+https://lexora.legal; Inteligencia de Fontes Oficiais)"
        }
        http_req = urllib.request.Request(target_url, headers=req_headers)

        start_time = time.time()
        captured_at = datetime.now(timezone.utc)

        try:
            with opener.open(http_req, timeout=request.timeout_seconds) as response:
                http_status = response.status
                content_type_raw = response.headers.get("Content-Type", "text/html; charset=utf-8")
                
                # Validação de MIME
                content_type_mime = content_type_raw.split(";")[0].strip().lower()
                if not any(allowed in content_type_mime for allowed in self.allowed_mimes):
                    raise UnsupportedContentTypeError(f"Tipo de conteúdo MIME '{content_type_raw}' não permitido para aquisição.")

                # Leitura limitada por bytes (streaming size cap)
                content_bytes = response.read(request.max_bytes + 1)
                if len(content_bytes) > request.max_bytes:
                    raise ArtifactTooLargeError(f"Artefato excede o limite máximo de {request.max_bytes} bytes.")

        except TimeoutError:
            raise AcquisitionTimeoutError(f"Tempo limite ({request.timeout_seconds}s) excedido para '{target_url}'.")
        except Exception as e:
            if isinstance(e, (SSRFProtectionError, RedirectNotAllowedError, UnsupportedContentTypeError, ArtifactTooLargeError, AcquisitionTimeoutError)):
                raise e
            raise AcquisitionFailedError(f"Falha na aquisição HTTP de '{target_url}': {str(e)}")

        response_time_ms = int((time.time() - start_time) * 1000)

        # 4. SHA-256 e DTOs Canônicos
        content_hash = hashlib.sha256(content_bytes).hexdigest()
        byte_size = len(content_bytes)

        artifact_id = f"artifact-{content_hash[:16]}"
        storage_key = f"sources/{source.id}/{artifact_id}.bin"

        artifact = RawArtifact(
            id=artifact_id,
            source_id=source.id,
            url=target_url,
            captured_at=captured_at,
            content_hash=content_hash,
            content_type=content_type_raw,
            size_bytes=byte_size,
            storage_key=storage_key,
            created_at=captured_at
        )

        change_status = ChangeStatus.NEW
        if request.expected_hash:
            if content_hash == request.expected_hash:
                change_status = ChangeStatus.UNCHANGED
            else:
                change_status = ChangeStatus.CHANGED

        audit_log = AcquisitionAuditLog(
            id=f"audit-{content_hash[:12]}",
            source_id=source.id,
            target_url=target_url,
            raw_artifact_id=artifact.id,
            http_status=http_status,
            content_type=content_type_raw,
            content_length=byte_size,
            content_hash=content_hash,
            response_time_ms=response_time_ms,
            change_status=change_status
        )

        return AcquisitionResult(
            artifact=artifact,
            audit_log=audit_log,
            content_bytes=content_bytes,
            redirect_chain=redirect_chain
        )
