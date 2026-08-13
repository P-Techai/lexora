from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class LegalEmbedding(BaseModel):
    """Entidade de Domínio para registro de vetores de embedding vinculados a um dispositivo normativo (LegalNode)."""
    model_config = ConfigDict(frozen=True)

    id: str
    legal_node_id: str
    legal_version_id: str
    legal_document_id: str
    content_hash: str
    embedding_model: str
    embedding_model_version: str
    dimensions: int
    vector: List[float] = Field(default_factory=list)
    created_at: Optional[datetime] = None
