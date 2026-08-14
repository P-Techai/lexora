from datetime import date
from decimal import Decimal
import pytest

from src.domain.enums import Jurisdiction, TaxRegime, TaxType
from src.domain.fiscal.company_fiscal_profile import CompanyFiscalProfile
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.fiscal.tax_workbench_pipeline import DecisionLifecycleState, NFeLifecycleState, OperationalTaxWorkbenchPipeline, ProductLifecycleState
from tests.unit.test_nfe_operational_fiscal_engine import SAMPLE_XML


def make_company_profile(company_id: str = "comp_golden_p9") -> CompanyFiscalProfile:
    return CompanyFiscalProfile(
        company_id=company_id,
        cnpj="12345678000190",
        corporate_name="EMPRESA GOLDEN WORKBENCH",
        state="SP",
        municipality="SAO PAULO",
        tax_regime=TaxRegime.LUCRO_REAL,
        valid_from=date(2020, 1, 1)
    )


def test_golden_phase9_01_complete_flow():
    """GOLDEN PHASE 9-01: Company -> Profile -> XML NF-e -> Validation -> Product Classification -> Rule -> Calculation -> Decision -> Report."""
    comp = make_company_profile()
    r_icms = FiscalTaxRule(rule_id="r_g9_icms", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, state="SP", effective_from=date(2026, 1, 1), rate=Decimal("18.00"), source_legal_node_id="n1", evidence_id="e1")
    r_pis = FiscalTaxRule(rule_id="r_g9_pis", tax_type=TaxType.PIS, jurisdiction=Jurisdiction.FEDERAL, effective_from=date(2026, 1, 1), rate=Decimal("1.65"), source_legal_node_id="n2", evidence_id="e2")
    r_cofins = FiscalTaxRule(rule_id="r_g9_cofins", tax_type=TaxType.COFINS, jurisdiction=Jurisdiction.FEDERAL, effective_from=date(2026, 1, 1), rate=Decimal("7.60"), source_legal_node_id="n3", evidence_id="e3")

    doc = OperationalTaxWorkbenchPipeline.process_nfe_workbench(
        xml_content=SAMPLE_XML,
        company_profile=comp,
        reference_date=date(2026, 8, 14),
        available_rules=[r_icms, r_pis, r_cofins]
    )

    assert doc.nfe_state == NFeLifecycleState.PROCESSED
    assert doc.review_required is False
    assert doc.total_invoice_amount == Decimal("5000.00")
    assert doc.total_tax_amount == Decimal("1362.50")
    assert doc.items[0].product_state == ProductLifecycleState.CLASSIFIED
    assert doc.items[0].decision_state == DecisionLifecycleState.CONFIRMED


def test_golden_phase9_02_expired_company_profile():
    """GOLDEN PHASE 9-02: Perfil fiscal de empresa expirado resulta em VALIDATION_FAILED."""
    expired_comp = CompanyFiscalProfile(
        company_id="comp_exp",
        cnpj="12345678000190",
        corporate_name="EMPRESA EXPIRADA LTDA",
        state="SP",
        municipality="SAO PAULO",
        tax_regime=TaxRegime.LUCRO_REAL,
        valid_from=date(2020, 1, 1),
        valid_until=date(2025, 12, 31)
    )

    r_icms = FiscalTaxRule(rule_id="r_g9_icms", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, state="SP", effective_from=date(2026, 1, 1), rate=Decimal("18.00"), source_legal_node_id="n1", evidence_id="e1")

    doc = OperationalTaxWorkbenchPipeline.process_nfe_workbench(
        xml_content=SAMPLE_XML,
        company_profile=expired_comp,
        reference_date=date(2026, 8, 14),
        available_rules=[r_icms]
    )

    assert doc.nfe_state == NFeLifecycleState.VALIDATION_FAILED
    assert doc.review_required is True
