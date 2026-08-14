from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import ClassificationStatus, ReviewStatus
from src.domain.fiscal.tax_calculation import TaxCalculation


class FiscalItemResult(BaseModel):
    """
    Resultado de classificação e apuração de um item fiscal individual.
    """
    model_config = ConfigDict(frozen=True)

    item_id: str = Field(..., description="ID do item")
    product_id: str = Field(..., description="ID do produto associado")
    classification_status: ClassificationStatus = Field(..., description="Status da classificação")
    ncm: str = Field(..., description="NCM de 8 dígitos")
    cest: Optional[str] = Field(None, description="CEST de 7 dígitos")
    cst: str = Field(..., description="CST de 2 ou 3 dígitos")
    csosn: Optional[str] = Field(None, description="CSOSN se Simples Nacional")
    cfop: str = Field(..., description="CFOP de 4 dígitos")
    tax_results: List[TaxCalculation] = Field(default_factory=list, description="Apuração individual por tributo")
    item_tax_total: Decimal = Field(..., description="Total acumulado dos tributos do item")
    review_status: ReviewStatus = Field(default=ReviewStatus.OPEN, description="Status de revisão se exigida")
    decision_id: str = Field(..., description="ID da decisão determinística gerada")


class FiscalDocumentResult(BaseModel):
    """
    Resultado de apuração consolidada do documento/operação fiscal.
    """
    model_config = ConfigDict(frozen=True)

    document_id: str = Field(..., description="ID do documento fiscal")
    company_id: str = Field(..., description="ID da empresa")
    operation_date: date = Field(..., description="Data da operação")
    items: List[FiscalItemResult] = Field(..., description="Lista de resultados por item")
    total_gross_amount: Decimal = Field(..., description="Valor total bruto do documento")
    total_tax_amount: Decimal = Field(..., description="Total consolidado dos tributos (derivado da soma dos itens)")
    tax_totals_by_type: Dict[str, Decimal] = Field(..., description="Consolidado por tributo (ICMS, PIS, COFINS, etc.)")
    decision_id: str = Field(..., description="ID da decisão mestre do documento")
    review_required: bool = Field(default=False, description="Flag indicando se há algum item pendente de revisão")
    engine_name: str = Field(default="LÉXORA Deterministic Tax Engine", description="Nome do motor de apuração")
    engine_version: str = Field(default="v0.12.0-fiscal-classification-tax-engine", description="Versão do motor de apuração")
