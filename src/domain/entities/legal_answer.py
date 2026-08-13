from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import LegalAnswerStatus, LegalNodeType


class LegalCitation(BaseModel):
    """Citação estruturada vinculada estritamente a um dispositivo normativo real e auditado."""
    model_config = ConfigDict(frozen=True)

    citation_id: str
    legal_node_id: str
    legal_version_id: str
    legal_document_id: str
    node_type: LegalNodeType
    identifier: str
    label: str
    excerpt: str
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None
    source_id: str
    evidence_id: str
    raw_artifact_hash: str


class LegalAnswer(BaseModel):
    """Resposta Jurídica Estruturada Auditável com Validação de Guardrails e Proveniência."""
    model_config = ConfigDict(frozen=True)

    answer_id: str
    query: str
    reference_date: date
    answer_text: str
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    status: LegalAnswerStatus = LegalAnswerStatus.SUPPORTED
    citations: List[LegalCitation] = Field(default_factory=list)
    supporting_nodes: List[str] = Field(default_factory=list)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    abstained: bool = False
    generated_at: Optional[datetime] = None
