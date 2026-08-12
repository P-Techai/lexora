from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import LegalRelationType


class LegalRelation(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    source_node_id: str
    target_node_id: str
    relation_type: LegalRelationType
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    evidence_id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
