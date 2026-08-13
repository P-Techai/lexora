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


class AnswerClaim(BaseModel):
    """Afirmação normativa individual contida na resposta textual, obrigatoriamente vinculada a citações."""
    model_config = ConfigDict(frozen=True)

    claim_id: str
    text: str
    citation_ids: List[str] = Field(default_factory=list)


class LegalAnswer(BaseModel):
    """Resposta Jurídica Estruturada Auditável com Validação de Guardrails e Proveniência."""
    model_config = ConfigDict(frozen=True)

    answer_id: str
    logical_answer_id: str
    query: str
    reference_date: date
    answer_text: str
    claims: List[AnswerClaim] = Field(default_factory=list)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    status: LegalAnswerStatus = LegalAnswerStatus.SUPPORTED
    citations: List[LegalCitation] = Field(default_factory=list)
    supporting_nodes: List[str] = Field(default_factory=list)
    provenance: Dict[str, Any] = Field(default_factory=dict)
    warnings: List[str] = Field(default_factory=list)
    conflicts: List[str] = Field(default_factory=list)
    abstained: bool = False
    provider_name: str = "mock-legal-generator"
    model_name: str = "default-model"
    model_version: str = "1.0.0"
    prompt_version: str = "1.0.0"
    generated_at: Optional[datetime] = None
