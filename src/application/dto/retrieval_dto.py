from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field

from src.domain.enums import DocumentType, Jurisdiction, LegalNodeType


class LegalRetrievalRequest(BaseModel):
    """Solicitação de busca híbrida jurídica com filtragem temporal e de jurisdição."""
    query: str
    reference_date: date
    jurisdiction: Optional[Jurisdiction] = None
    document_type: Optional[DocumentType] = None
    document_number: Optional[str] = None
    top_k: int = Field(default=10, ge=1, le=100, description="Número máximo de candidatos retornados (1 a 100)")


class LegalRetrievalResultItem(BaseModel):
    """Item individual do resultado de busca híbrida com proveniência e pontuação detalhada."""
    legal_node_id: str
    legal_version_id: str
    legal_document_id: str
    node_type: LegalNodeType
    identifier: str
    label: str
    text: str
    path: str
    hierarchical_context: str
    lexical_score: float
    semantic_score: float
    final_score: float
    source_id: str
    evidence_id: Optional[str] = None
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None
    content_hash: str
    provenance_chain: dict = Field(default_factory=dict, description="Cadeia de proveniência em 5 níveis auditada")


class LegalRetrievalResultResponse(BaseModel):
    """Resposta agregada da busca híbrida jurídica."""
    query: str
    normalized_query: str
    reference_date: date
    results: List[LegalRetrievalResultItem]
    total_candidates: int
    provenance_valid: bool = True
