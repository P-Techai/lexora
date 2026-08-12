from datetime import date, datetime
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
    created_at: Optional[datetime] = None

    def is_effective_on(self, target_date: date) -> bool:
        """Verifica se a versão estava vigente na data informada."""
        if self.status != VersionStatus.ACTIVE:
            return False
        if self.effective_from is not None and target_date < self.effective_from:
            return False
        if self.effective_until is not None and target_date > self.effective_until:
            return False
        return True
