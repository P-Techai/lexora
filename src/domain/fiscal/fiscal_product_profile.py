from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import ClassificationStatus


class FiscalProductProfile(BaseModel):
    """
    Perfil fiscal determinístico do produto.
    """
    model_config = ConfigDict(frozen=True)

    product_id: str = Field(..., description="ID único do produto")
    sku: Optional[str] = Field(None, description="SKU do produto")
    gtin: Optional[str] = Field(None, description="GTIN / EAN de 13 dígitos")
    description: str = Field(..., description="Descrição original recebida do item")
    normalized_description: str = Field(..., description="Descrição normalizada em maiúsculas sem acentos")
    ncm: Optional[str] = Field(None, description="NCM de 8 dígitos numéricos")
    cest: Optional[str] = Field(None, description="CEST de 7 dígitos numéricos se aplicável")
    ean: Optional[str] = Field(None, description="Código de barras EAN")
    unit: str = Field(default="UN", description="Unidade comercial")
    origin: int = Field(default=0, ge=0, le=8, description="Origem da mercadoria (0 a 8)")
    manufacturer: Optional[str] = Field(None, description="Fabricante do produto")
    brand: Optional[str] = Field(None, description="Marca do produto")
    category: Optional[str] = Field(None, description="Categoria fiscal do produto")
    product_attributes: Dict[str, Any] = Field(default_factory=dict, description="Atributos técnicos adicionais")
    fiscal_status: ClassificationStatus = Field(default=ClassificationStatus.UNCLASSIFIED, description="Status da classificação")
    classification_confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Métrica técnica de confiança")
    classification_source: str = Field(default="DOCUMENT_ORIGIN", description="Fonte da classificação (ex: DOCUMENT_ORIGIN, LEGAL_RULE, MANUAL_REVIEW)")
