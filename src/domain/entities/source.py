from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import Jurisdiction


class Source(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    official: bool = True
    authority_level: int = Field(default=1, ge=1, le=5)  # 1 (Primária) a 5 (Comunitária) - ADR-0008
    trust_score: float = Field(default=1.0, ge=0.0, le=1.0) # Confiabilidade operacional (0.0 a 1.0)
    base_url: Optional[str] = None
    jurisdiction: Jurisdiction = Jurisdiction.FEDERAL
    active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
