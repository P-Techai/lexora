from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class RawArtifact(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    source_id: str
    url: str
    captured_at: datetime
    content_hash: str
    content_type: str
    size_bytes: int
    storage_key: str
    created_at: Optional[datetime] = None
