from datetime import date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.application.dto.retrieval_dto import LegalRetrievalResultItem


class LegalContextPack(BaseModel):
    """Pacote de Contexto Jurídico Fechado e Determinístico para Geração Linguística Controlada."""
    model_config = ConfigDict(frozen=True)

    pack_id: str
    query: str
    normalized_query: str
    reference_date: date
    retrieval_results: List[LegalRetrievalResultItem] = Field(default_factory=list)
    selected_nodes: List[LegalRetrievalResultItem] = Field(default_factory=list)
    canonical_context_text: str
    temporal_status: str = "EFFECTIVE"
    provenance_summary: Dict[str, Any] = Field(default_factory=dict)
    conflicts: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    total_characters: int = 0
