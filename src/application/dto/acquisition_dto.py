from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AcquisitionRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str
    url: str
    max_size_bytes: int = Field(default=25_000_000, gt=0)  # 25 MB padrão
    timeout_seconds: float = Field(default=30.0, gt=0.0)
    allowed_content_types: List[str] = Field(
        default_factory=lambda: [
            "text/plain",
            "text/html",
            "application/pdf",
            "text/xml",
            "application/xml",
            "application/json",
        ]
    )


class AcquisitionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str
    url: str
    status_code: int
    content_type: str
    size_bytes: int
    raw_bytes: bytes
    content_hash: str
    captured_at: datetime
    redirect_chain: List[str] = Field(default_factory=list)
    headers: Dict[str, str] = Field(default_factory=dict)
