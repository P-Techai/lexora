from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class Evidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    source_id: str
    legal_document_id: Optional[str] = None
    legal_version_id: Optional[str] = None
    legal_node_id: Optional[str] = None
    source_url: Optional[str] = None
    quote_or_excerpt: str
    locator: Optional[str] = None  # Ex: "Página 14, Coluna 2, Parágrafo 3"
    content_hash: str
    captured_at: datetime
    created_at: Optional[datetime] = None
