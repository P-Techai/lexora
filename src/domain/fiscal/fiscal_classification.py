from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import ClassificationStatus


class FiscalClassification(BaseModel):
    """
    Entidade de classificação fiscal determinística de produto e operação.
    Separa estritamente semantic_confidence, legal_confidence e calculation_confidence.
    """
    model_config = ConfigDict(frozen=True)

    classification_id: str = Field(..., description="ID da classificação")
    ncm: str = Field(..., description="NCM classificado")
    cst: Optional[str] = Field(None, description="CST classificado")
    cfop: Optional[str] = Field(None, description="CFOP classificado")
    status: ClassificationStatus = Field(..., description="Status (CONFIRMED, PROVISIONAL, REVIEW_REQUIRED, UNKNOWN)")
    reasons: List[str] = Field(default_factory=list, description="Motivos e justificativas da classificação")
    legal_node_id: Optional[str] = Field(None, description="Fundamentação jurídica da classificação")
    semantic_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confiança na interpretação semântica")
    legal_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confiança na fundamentação jurídica (exige vinculação a Nó Legal)")
    calculation_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confiança no resultado do cálculo determinístico")
