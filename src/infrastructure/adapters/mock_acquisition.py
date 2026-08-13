from datetime import datetime, timezone
import hashlib
from typing import Optional, Tuple

from src.application.dto.acquisition_dto import AcquisitionRequest, AcquisitionResult
from src.application.ports.acquisition_provider import DocumentAcquisitionProvider
from src.domain.entities.acquisition_audit_log import AcquisitionAuditLog
from src.domain.entities.raw_artifact import RawArtifact
from src.domain.entities.source import Source
from src.domain.enums import ChangeStatus


class MockDocumentAcquisitionAdapter(DocumentAcquisitionProvider):
    """Adaptador mock para aquisição determinística de artefatos brutos em ambiente de testes unitários."""

    def __init__(self, mock_content: Optional[bytes] = None, mock_status: int = 200):
        self.mock_content = mock_content or b"Conteudo sintetico de teste oficial LEXORA."
        self.mock_status = mock_status

    async def acquire(self, request: AcquisitionRequest) -> AcquisitionResult:
        captured_at = datetime.now(timezone.utc)
        content_hash = hashlib.sha256(self.mock_content).hexdigest()
        byte_size = len(self.mock_content)

        artifact_id = f"artifact-{content_hash[:16]}"
        storage_key = f"sources/{request.source.id}/{artifact_id}.bin"

        artifact = RawArtifact(
            id=artifact_id,
            source_id=request.source.id,
            url=request.target_url,
            captured_at=captured_at,
            content_hash=content_hash,
            content_type="text/html; charset=utf-8",
            size_bytes=byte_size,
            storage_key=storage_key,
            created_at=captured_at
        )

        change_status = ChangeStatus.NEW
        if request.expected_hash:
            change_status = ChangeStatus.UNCHANGED if content_hash == request.expected_hash else ChangeStatus.CHANGED

        audit_log = AcquisitionAuditLog(
            id=f"audit-{content_hash[:12]}",
            source_id=request.source.id,
            target_url=request.target_url,
            raw_artifact_id=artifact.id,
            http_status=self.mock_status,
            content_type="text/html; charset=utf-8",
            content_length=byte_size,
            content_hash=content_hash,
            response_time_ms=10,
            change_status=change_status
        )

        return AcquisitionResult(
            artifact=artifact,
            audit_log=audit_log,
            content_bytes=self.mock_content,
            redirect_chain=[request.target_url]
        )
