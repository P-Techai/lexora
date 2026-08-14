from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import ClassificationStatus


class FiscalProductProfile(BaseModel):
    """
    Perfil e classificação fiscal consolidada de produto.
    NUNCA trata UNKNOWN como CONFIRMED. Exige status de classificação explícito.
    """
    model_config = ConfigDict(frozen=True)

    product_id: str = Field(..., description="ID ou código interno do produto")
    ncm: str = Field(..., description="Código NCM")
    cest: Optional[str] = Field(None, description="Código CEST")
    ex_tipi: Optional[str] = Field(None, description="Exceção da TIPI se aplicável")
    origin: int = Field(default=0, ge=0, le=8, description="Origem da mercadoria")
    product_description: str = Field(..., description="Descrição original do produto")
    normalized_description: str = Field(..., description="Descrição normalizada para matching")
    fiscal_category: Optional[str] = Field(None, description="Categoria fiscal atribuída")
    classification_status: ClassificationStatus = Field(
        default=ClassificationStatus.UNKNOWN,
        description="Status da classificação (CONFIRMED, PROVISIONAL, REVIEW_REQUIRED, UNKNOWN)"
    )
