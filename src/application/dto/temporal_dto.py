from datetime import date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.entities.evidence import Evidence
from src.domain.entities.legal_node import LegalNode
from src.domain.entities.legal_relation import LegalRelation
from src.domain.entities.legal_version import LegalVersion
from src.domain.enums import TemporalStatus


class TemporalQueryRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    document_id: str
    target_date: date  # Obrigatoriamente fornecida (nunca datetime.now() implícito)
    include_nodes: bool = True
    include_relations: bool = True


class TemporalLegalResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: TemporalStatus
    document_id: str
    target_date: date
    version_id: Optional[str] = None
    version: Optional[LegalVersion] = None
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None
    nodes: List[LegalNode] = Field(default_factory=list)
    relations: List[LegalRelation] = Field(default_factory=list)
    evidences: List[Evidence] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
