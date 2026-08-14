from datetime import date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import Jurisdiction, TaxType
from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.services.fiscal.tax_rule_evaluator import TaxRuleEvaluator
from src.domain.services.temporal_validator import TemporalIntegrityValidator


class ResolvedTaxRule(BaseModel):
    """
    Regra fiscal resolvida com fundamentação legal e justificativa de aplicabilidade.
    """
    model_config = ConfigDict(frozen=True)

    rule_id: str
    tax_type: TaxType
    jurisdiction: Jurisdiction
    effective_from: date
    effective_until: Optional[date] = None
    legal_node_id: Optional[str] = None
    evidence_id: Optional[str] = None
    priority: int
    applicability_reason: str


class TaxRuleResolver:
    """
    Resolvedor determinístico de regras fiscais com base na data da operação e na hierarquia normativa.
    """

    @staticmethod
    def resolve_rules_for_fact(fact: FiscalFact, available_rules: List[FiscalTaxRule]) -> List[ResolvedTaxRule]:
        # 1. Filtra temporalmente usando a data de operação como autoridade temporal (§19)
        active_rules: List[FiscalTaxRule] = []
        for r in available_rules:
            is_valid, _ = TemporalIntegrityValidator.is_date_in_range(fact.operation_date, r.effective_from, r.effective_until)
            if is_valid:
                active_rules.append(r)

        # 2. Encontra regras compatíveis com o fato fiscal
        matching = TaxRuleEvaluator.find_matching_rules(fact, active_rules)

        resolved: List[ResolvedTaxRule] = []
        for m in matching:
            resolved.append(ResolvedTaxRule(
                rule_id=m.rule_id,
                tax_type=m.tax_type,
                jurisdiction=m.jurisdiction,
                effective_from=m.effective_from,
                effective_until=m.effective_until,
                legal_node_id=m.source_legal_node_id,
                evidence_id=m.evidence_id,
                priority=m.priority,
                applicability_reason=f"Regra {m.rule_id} aplicável para {m.tax_type.value} na UF {m.state or 'BR'} na data {fact.operation_date}"
            ))

        return resolved
