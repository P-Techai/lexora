from datetime import date
from typing import List

from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.services.temporal_validator import TemporalIntegrityValidator


class TaxRuleEvaluator:
    """
    Avaliador determinístico de regras tributárias com validação temporal rigorosa.
    Utiliza TemporalIntegrityValidator.is_date_in_range() contra fact.operation_date.
    NUNCA utiliza datetime.now() ou date.today().
    """

    @staticmethod
    def is_rule_temporally_valid(rule: FiscalTaxRule, reference_date: date) -> bool:
        """
        Verifica se a regra fiscal é temporalmente válida no intervalo [effective_from, effective_until) na data de referência.
        """
        return TemporalIntegrityValidator.is_date_in_range(
            target_date=reference_date,
            effective_from=rule.effective_from,
            effective_until=rule.effective_until
        )

    @classmethod
    def find_matching_rules(cls, fact: FiscalFact, available_rules: List[FiscalTaxRule]) -> List[FiscalTaxRule]:
        """
        Filtra regras fiscais que correspondem ao fato fiscal e são válidas em fact.operation_date.
        """
        matching: List[FiscalTaxRule] = []

        for rule in available_rules:
            # 1. Validação temporal estrita contra operation_date
            if not cls.is_rule_temporally_valid(rule, fact.operation_date):
                continue

            # 2. Validação de jurisdição e UF
            if rule.state and rule.state != fact.state and rule.state != fact.destination_state:
                continue

            # 3. Match de condições
            conditions_match = True
            for field, expected in rule.conditions.items():
                fact_val = getattr(fact, field, None)
                if fact_val is None and field in fact.additional_fields:
                    fact_val = fact.additional_fields[field]
                
                if isinstance(expected, list):
                    if fact_val not in expected:
                        conditions_match = False
                        break
                elif fact_val != expected:
                    conditions_match = False
                    break

            if conditions_match:
                matching.append(rule)

        # Ordenação determinística por prioridade (menor número = maior prioridade) e id da regra
        matching.sort(key=lambda r: (r.priority, r.rule_id))
        return matching
