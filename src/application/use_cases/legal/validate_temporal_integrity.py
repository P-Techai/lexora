from typing import Tuple

from src.application.ports.repositories import LegalVersionRepository
from src.domain.enums import TemporalStatus
from src.domain.services.temporal_validator import TemporalIntegrityValidator


class ValidateTemporalIntegrityUseCase:
    """Caso de uso para auditar e validar a integridade da série de versões de um documento."""

    def __init__(self, version_repo: LegalVersionRepository):
        self.version_repo = version_repo

    async def execute(self, document_id: str) -> Tuple[TemporalStatus, list[str]]:
        versions = await self.version_repo.get_versions_by_document(document_id)
        return TemporalIntegrityValidator.audit_version_series(versions)
