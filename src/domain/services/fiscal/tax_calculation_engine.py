import uuid
from decimal import Decimal
from typing import Dict, List, Tuple

from src.domain.enums import TaxType
from src.domain.fiscal.calculation_memory import CalculationMemory
from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.fiscal.tax_calculation import TaxCalculation
from src.domain.services.fiscal.tax_calculator import TaxCalculator


class TaxCalculationEngine:
    """
    Motor determinístico de cálculo e geração de memória fiscal.
    Suporta ICMS, ICMS_ST, IPI, PIS, COFINS, ISS, CBS, IBS, IS, FCP, FCP_ST.
    """

    @staticmethod
    def calculate_taxes_for_fact(
        fact: FiscalFact,
        rules: List[FiscalTaxRule]
    ) -> Tuple[List[TaxCalculation], List[CalculationMemory]]:
        calculations: List[TaxCalculation] = []
        memories: List[CalculationMemory] = []

        for rule in rules:
            calc = TaxCalculator.calculate_tax(fact, rule)
            calculations.append(calc)

            inputs_snapshot: Dict[str, str] = {
                "quantity": str(fact.quantity),
                "unit_value": str(fact.unit_value),
                "total_value": str(fact.total_value),
                "base_reduction": str(rule.base_reduction),
                "rate": str(rule.rate)
            }

            formula_text = (
                f"taxable_base = total_value ({fact.total_value}) * (1 - reduction ({rule.base_reduction})/100); "
                f"amount = round_half_up(taxable_base * rate ({rule.rate})/100)"
            )

            calc_mem = CalculationMemory.create(
                calculation_id=f"calc_mem_{uuid.uuid4().hex[:8]}",
                operation_id=fact.fact_id,
                item_id=fact.fact_id,
                tax_type=rule.tax_type,
                taxable_base=calc.taxable_base,
                rate=calc.rate,
                calculated_amount=calc.calculated_amount,
                inputs=inputs_snapshot,
                formula=formula_text,
                rule_id=rule.rule_id,
                legal_reference=calc.legal_basis,
                evidence_id=rule.evidence_id
            )
            memories.append(calc_mem)

        return calculations, memories
