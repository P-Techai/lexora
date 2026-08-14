from datetime import date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import DecisionStatus
from src.domain.fiscal.fiscal_classification import FiscalClassification
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.fiscal.tax_calculation import TaxCalculation


class Decision(BaseModel):
    """
    Entidade de Decisão Tributária Determinística consolidada pelo Decision Engine.
    """
    model_config = ConfigDict(frozen=True)

    decision_id: str = Field(..., description="ID determinístico SHA-256 da decisão")
    status: DecisionStatus = Field(..., description="Status final (APPROVED, REVIEW_REQUIRED, CONFLICT, INSUFFICIENT_DATA, NO_APPLICABLE_RULE)")
    classification: FiscalClassification = Field(..., description="Classificação fiscal resultante")
    tax_results: List[TaxCalculation] = Field(default_factory=list, description="Lista de cálculos de impostos efetuados")
    applied_rules: List[FiscalTaxRule] = Field(default_factory=list, description="Regras fiscais aplicadas")
    legal_basis: List[Dict[str, Any]] = Field(default_factory=list, description="Fundamentação legal associada")
    warnings: List[str] = Field(default_factory=list, description="Alertas e observações operacionais")
    conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Conflitos normativos ou de regras detectados")
    review_required: bool = Field(default=False, description="Flag indicando necessidade de revisão humana")
    decision_trace: Optional[Dict[str, Any]] = Field(None, description="Árvore de decisão estruturada")
    reference_date: date = Field(..., description="Data de referência temporal avaliada")
    decision_hash: str = Field(..., description="Hash SHA-256 final da decisão para reprodutibilidade")
