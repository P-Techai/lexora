from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class AcquisitionAuditLog(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    source_id: str
    url: str
    status_code: Optional[int] = None
    success: bool
    error_message: Optional[str] = None  # Sempre higienizado (sem segredos/tokens)
    content_hash: Optional[str] = None
    captured_at: datetime
    created_at: Optional[datetime] = None
