from decimal import Decimal

from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.fiscal.tax_calculation import TaxCalculation
from src.domain.services.fiscal.tax_base_calculator import TaxBaseCalculator
from src.domain.services.fiscal.tax_rounding_service import TaxRoundingService


class TaxCalculator:
    """
    Motor determinístico de cálculo de tributos (ICMS, ICMS_ST, IPI, PIS, COFINS, ISS, CBS, IBS, IS).
    A alíquota e regras vem EXCLUSIVAMENTE da FiscalTaxRule (nunca hardcodadas em código ou env).
    """

    @staticmethod
    def calculate_tax(fact: FiscalFact, rule: FiscalTaxRule) -> TaxCalculation:
        """
        Executa o cálculo tributário determinístico.
        """
        taxable_base, reduction_amount = TaxBaseCalculator.calculate_taxable_base(fact, rule)

        if rule.is_exempt or taxable_base == Decimal("0.00"):
            calculated_amount = Decimal("0.00")
        else:
            raw_amount = taxable_base * (rule.rate / Decimal("100.00"))
            calculated_amount = TaxRoundingService.round_amount(raw_amount)

        legal_basis = {}
        if rule.source_legal_node_id:
            legal_basis = {
                "source_legal_node_id": rule.source_legal_node_id,
                "source_legal_version_id": rule.source_legal_version_id,
                "evidence_id": rule.evidence_id,
            }

        return TaxCalculation(
            tax_type=rule.tax_type,
            taxable_base=taxable_base,
            rate=rule.rate,
            base_reduction=rule.base_reduction,
            calculated_amount=calculated_amount,
            rounding=Decimal("0.00"),
            formula=rule.formula,
            inputs={
                "fact_id": fact.fact_id,
                "total_value": str(fact.total_value),
                "reduction_amount": str(reduction_amount),
            },
            rule_id=rule.rule_id,
            legal_basis=legal_basis,
            reference_date=fact.operation_date
        )
