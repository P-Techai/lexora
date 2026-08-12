from datetime import datetime
from typing import Optional
import uuid

from src.application.dto.acquisition_dto import AcquisitionRequest, AcquisitionResult
from src.application.ports.acquisition_provider import DocumentAcquisitionProvider
from src.application.ports.repositories import SourceRepository
from src.application.ports.storage_provider import StorageProvider
from src.application.services.source_registry import SourceRegistryService
from src.domain.entities.acquisition_audit_log import AcquisitionAuditLog
from src.domain.entities.raw_artifact import RawArtifact
from src.domain.services.url_validator import URLSecurityValidator


class AcquireArtifactUseCase:
    """Caso de Uso para Aquisição Controlada, Validação SSRF, Armazenamento Raw e Registro de Auditoria."""

    def __init__(
        self,
        acquisition_provider: DocumentAcquisitionProvider,
        source_registry: SourceRegistryService,
        storage_provider: StorageProvider,
    ):
        self.acquisition_provider = acquisition_provider
        self.source_registry = source_registry
        self.storage_provider = storage_provider

    async def execute(self, request: AcquisitionRequest) -> tuple[RawArtifact, AcquisitionAuditLog]:
        # 1. Validação de Fonte Ativa e Política
        source = await self.source_registry.validate_source_active_and_policy(request.source_id)

        # 2. Validação da URL e Proteção SSRF
        allowed_domains = self.source_registry.get_allowed_domains(request.source_id)
        validated_url = URLSecurityValidator.validate_url(request.url, allowed_domains=allowed_domains)

        captured_at = datetime.utcnow()
        audit_log = None
        raw_artifact = None

        try:
            # 3. Execução da Aquisição via Porta Abstrata
            result: AcquisitionResult = await self.acquisition_provider.acquire(request)

            # 4. Gravação do Artefato Bruto no Storage (Local / Cloudflare R2 / S3)
            storage_key = f"artifacts/{request.source_id}/{result.content_hash}.bin"
            await self.storage_provider.save_bytes(storage_key, result.raw_bytes, result.content_type)

            raw_artifact = RawArtifact(
                id=str(uuid.uuid4()),
                source_id=request.source_id,
                url=validated_url,
                captured_at=result.captured_at,
                content_hash=result.content_hash,
                content_type=result.content_type,
                size_bytes=result.size_bytes,
                storage_key=storage_key
            )

            audit_log = AcquisitionAuditLog(
                id=str(uuid.uuid4()),
                source_id=request.source_id,
                url=validated_url,
                status_code=result.status_code,
                success=True,
                error_message=None,
                content_hash=result.content_hash,
                captured_at=captured_at
            )

            return raw_artifact, audit_log

        except Exception as e:
            # Sanitização do erro para auditoria (evita vazamento de segredos)
            clean_error = str(e)[:255]
            audit_log = AcquisitionAuditLog(
                id=str(uuid.uuid4()),
                source_id=request.source_id,
                url=validated_url,
                status_code=None,
                success=False,
                error_message=clean_error,
                content_hash=None,
                captured_at=captured_at
            )
            raise e
