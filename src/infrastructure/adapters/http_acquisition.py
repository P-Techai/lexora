from datetime import datetime, timezone
import hashlib
import time
import urllib.request
import urllib.parse
from typing import Optional, Tuple

from src.application.ports.acquisition_provider import DocumentAcquisitionProvider
from src.application.services.source_registry import SourceRegistryService
from src.domain.entities.acquisition_audit_log import AcquisitionAuditLog
from src.domain.entities.raw_artifact import RawArtifact
from src.domain.entities.source import Source
from src.domain.enums import ChangeStatus
from src.domain.exceptions import AcquisitionFailedError, ArtifactTooLargeError, SSRFProtectionError


class HttpDocumentAcquisitionAdapter(DocumentAcquisitionProvider):
    """Adaptador de aquisição HTTP real para coleta oficial de artefatos com proteção SSRF e rate limit."""

    def __init__(self, source_registry: SourceRegistryService, max_bytes: int = 50 * 1024 * 1024):
        self.source_registry = source_registry
        self.max_bytes = max_bytes
        self._last_request_time = 0.0

    async def acquire_document(
        self,
        source: Source,
        target_url: str,
        expected_hash: Optional[str] = None
    ) -> Tuple[RawArtifact, AcquisitionAuditLog, bytes]:
        # 1. Validação de Segurança SSRF e Governança da Fonte
        url_valid, url_warnings = self.source_registry.validate_acquisition_url(source, target_url)
        if not url_valid:
            raise SSRFProtectionError(f"Segurança SSRF: URL '{target_url}' rejeitada para a fonte '{source.name}': {url_warnings}")

        # 2. Rate Limiting Polido (máximo 2 requisições/s)
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < 0.5:
            time.sleep(0.5 - elapsed)
        self._last_request_time = time.time()

        # 3. Requisição HTTP Real
        req = urllib.request.Request(
            target_url,
            headers={
                "User-Agent": "LEXORA-Bot/1.0 (+https://lexora.legal; Inteligencia de Fontes Oficiais)"
            }
        )

        start_time = time.time()
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                http_status = response.status
                content_type = response.headers.get("Content-Type", "text/html; charset=utf-8")
                content_bytes = response.read(self.max_bytes + 1)
                
                if len(content_bytes) > self.max_bytes:
                    raise ArtifactTooLargeError(f"Artefato excede o limite máximo de {self.max_bytes} bytes.")
        except Exception as e:
            if isinstance(e, (SSRFProtectionError, ArtifactTooLargeError)):
                raise e
            raise AcquisitionFailedError(f"Falha na aquisição HTTP de '{target_url}': {str(e)}")

        response_time_ms = int((time.time() - start_time) * 1000)

        # 4. Cálculo SHA-256
        content_hash = hashlib.sha256(content_bytes).hexdigest()
        byte_size = len(content_bytes)

        artifact_id = f"artifact-{content_hash[:16]}"
        storage_key = f"sources/{source.id}/{artifact_id}.bin"

        artifact = RawArtifact(
            id=artifact_id,
            source_id=source.id,
            source_url=target_url,
            content_hash=content_hash,
            byte_size=byte_size,
            content_type=content_type,
            storage_key=storage_key,
            captured_at=datetime.now(timezone.utc).date()
        )

        audit_log = AcquisitionAuditLog(
            id=f"audit-{content_hash[:12]}",
            source_id=source.id,
            target_url=target_url,
            raw_artifact_id=artifact.id,
            http_status=http_status,
            content_type=content_type,
            content_length=byte_size,
            content_hash=content_hash,
            response_time_ms=response_time_ms,
            change_status=ChangeStatus.NEW if not expected_hash else (
                ChangeStatus.UNCHANGED if content_hash == expected_hash else ChangeStatus.UPDATED
            )
        )

        return artifact, audit_log, content_bytes
