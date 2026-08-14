from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.decision.decision import Decision
from src.domain.enums import DecisionStatus, DivergenceSeverity, DivergenceStatus, TaxType


class Divergence(BaseModel):
    """
    Entidade representando uma divergência fiscal auditável.
    """
    model_config = ConfigDict(frozen=True)

    divergence_id: str = Field(..., description="ID da divergência")
    decision_id: str = Field(..., description="ID da decisão associada")
    fact_id: str = Field(..., description="ID do fato fiscal")
    tax_type: TaxType = Field(..., description="Tipo de tributo afetado")
    expected_value: Optional[Decimal] = Field(None, description="Valor esperado")
    calculated_value: Optional[Decimal] = Field(None, description="Valor calculado")
    difference: Optional[Decimal] = Field(None, description="Diferença apurada")
    rule_id: Optional[str] = Field(None, description="ID da regra fiscal envolvida")
    legal_reference: Optional[str] = Field(None, description="Referência jurídica vinculada")
    severity: DivergenceSeverity = Field(..., description="Severidade (INFO, WARNING, CRITICAL)")
    status: DivergenceStatus = Field(default=DivergenceStatus.OPEN, description="Status da divergência")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class DivergenceEngine:
    """
    Motor determinístico para identificação e classificação de divergências tributárias.
    """

    @staticmethod
    def detect_divergences(decision: Decision, expected_taxes: Optional[Dict[str, Decimal]] = None) -> List[Divergence]:
        divergences: List[Divergence] = []

        # 1. Checa conflito de regras (Severidade CRITICAL)
        if decision.status in (DecisionStatus.CONFLICT, DecisionStatus.FISCAL_RULE_CONFLICT):
            divergences.append(Divergence(
                divergence_id=f"div_conf_{decision.decision_id[4:]}",
                decision_id=decision.decision_id,
                fact_id=decision.decision_trace.get("fact_id", "unknown_fact"),
                tax_type=TaxType.ICMS,
                severity=DivergenceSeverity.CRITICAL,
                legal_reference="Conflito normativo entre regras ativas de mesma prioridade"
            ))

        # 2. Checa ausência de fundamentação legal (Severidade CRITICAL)
        if decision.status in (DecisionStatus.LEGAL_BASIS_MISSING, DecisionStatus.INSUFFICIENT_LEGAL_BASIS):
            divergences.append(Divergence(
                divergence_id=f"div_leg_{decision.decision_id[4:]}",
                decision_id=decision.decision_id,
                fact_id=decision.decision_trace.get("fact_id", "unknown_fact"),
                tax_type=TaxType.ICMS,
                severity=DivergenceSeverity.CRITICAL,
                legal_reference="Fundamentação legal ausente ou insuficiente"
            ))

        # 3. Compara valores esperados vs calculados se fornecido
        if expected_taxes:
            for calc in decision.tax_results:
                tax_key = calc.tax_type.value
                if tax_key in expected_taxes:
                    exp_val = expected_taxes[tax_key]
                    calc_val = calc.calculated_amount
                    diff = abs(exp_val - calc_val)
                    if diff > Decimal("0.00"):
                        severity = DivergenceSeverity.WARNING if diff < Decimal("50.00") else DivergenceSeverity.CRITICAL
                        divergences.append(Divergence(
                            divergence_id=f"div_val_{decision.decision_id[4:]}_{tax_key}",
                            decision_id=decision.decision_id,
                            fact_id=decision.decision_trace.get("fact_id", "unknown_fact"),
                            tax_type=calc.tax_type,
                            expected_value=exp_val,
                            calculated_value=calc_val,
                            difference=diff,
                            severity=severity
                        ))

        return divergences
