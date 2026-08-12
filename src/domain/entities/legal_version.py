from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict

from src.domain.enums import VersionStatus


class LegalVersion(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    legal_document_id: str
    version_number: int = 1
    content_hash: str
    published_at: Optional[date] = None
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None
    status: VersionStatus = VersionStatus.ACTIVE
    source_document_url: Optional[str] = None
    raw_storage_key: Optional[str] = None
    parser_version: str = "1.0.0"

    def is_effective_on(self, target_date: date) -> bool:
        """
        Delega para a única fonte de verdade temporal do domínio:
        TemporalIntegrityValidator.is_date_in_range [effective_from, effective_until).
        """
        from src.domain.services.temporal_validator import TemporalIntegrityValidator
        return TemporalIntegrityValidator.is_date_in_range(
            target_date=target_date,
            effective_from=self.effective_from,
            effective_until=self.effective_until
        )
