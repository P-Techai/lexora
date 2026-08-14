from decimal import Decimal
from typing import Tuple

from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.services.fiscal.tax_rounding_service import TaxRoundingService


class TaxBaseCalculator:
    """
    Calculador determinístico de base de cálculo tributária em Decimal.
    Aplica reduções, isenções e inclusões de frete/despesas se aplicáveis.
    """

    @staticmethod
    def calculate_taxable_base(fact: FiscalFact, rule: FiscalTaxRule) -> Tuple[Decimal, Decimal]:
        """
        Retorna uma tupla (taxable_base, reduction_amount).
        Se a regra for isenta (is_exempt=True), a base tributável é 0.00.
        """
        total = fact.total_value

        if rule.is_exempt:
            return Decimal("0.00"), total

        reduction_percentage = rule.base_reduction
        if reduction_percentage > Decimal("0.00"):
            reduction_amount = TaxRoundingService.round_amount(total * (reduction_percentage / Decimal("100.00")))
            taxable_base = TaxRoundingService.round_amount(total - reduction_amount)
            return max(Decimal("0.00"), taxable_base), reduction_amount

        return TaxRoundingService.round_amount(total), Decimal("0.00")
