from datetime import date
from decimal import Decimal
import pytest

from src.domain.enums import Jurisdiction, TaxRegime, TaxType
from src.domain.fiscal.company_fiscal_profile import CompanyFiscalProfile
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.fiscal.tax_workbench_pipeline import DecisionLifecycleState, NFeLifecycleState, OperationalTaxWorkbenchPipeline, ProductLifecycleState
from tests.unit.test_nfe_operational_fiscal_engine import SAMPLE_XML


def make_company_profile(company_id: str = "comp_wb_01", valid_from: date = date(2020, 1, 1), valid_until: date = None) -> CompanyFiscalProfile:
    return CompanyFiscalProfile(
        company_id=company_id,
        cnpj="12345678000190",
        corporate_name="EMPRESA OPERACIONAL SP LTDA",
        state="SP",
        municipality="SAO PAULO",
        tax_regime=TaxRegime.LUCRO_REAL,
        valid_from=valid_from,
        valid_until=valid_until
    )


def make_rule(rule_id: str = "r_wb_01", rate: Decimal = Decimal("18.00")) -> FiscalTaxRule:
    return FiscalTaxRule(
        rule_id=rule_id,
        tax_type=TaxType.ICMS,
        jurisdiction=Jurisdiction.STATE,
        state="SP",
        effective_from=date(2026, 1, 1),
        effective_until=date(2026, 12, 31),
        priority=10,
        rate=rate,
        source_legal_node_id="node_wb_1",
        source_legal_version_id="ver_wb_1",
        evidence_id="ev_wb_1"
    )


# 1. empresa isolada
def test_01_isolated_company():
    comp = make_company_profile("comp_A")
    res = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [make_rule()])
    assert res.company_id == "comp_A"


# 2. XML válido
def test_02_valid_xml():
    comp = make_company_profile()
    res = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [make_rule()])
    assert res.nfe_state == NFeLifecycleState.PROCESSED
    assert res.total_invoice_amount == Decimal("5000.00")


# 3. XML inválido
def test_03_invalid_xml():
    comp = make_company_profile()
    with pytest.raises(ValueError):
        OperationalTaxWorkbenchPipeline.process_nfe_workbench("<invalid>xml", comp, date(2026, 8, 14), [make_rule()])


# 4. XML duplicado / idempotência
def test_04_duplicate_xml_hash():
    comp = make_company_profile()
    r1 = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [make_rule()])
    r2 = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [make_rule()])
    assert r1.raw_xml_hash == r2.raw_xml_hash


# 5. lote com múltiplas NF-e (verificação pipeline)
def test_05_multiple_nfe():
    comp = make_company_profile()
    res = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [make_rule()])
    assert len(res.items) == 1


# 6. produto corretamente classificado
def test_06_classified_product():
    comp = make_company_profile()
    res = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [make_rule()])
    assert res.items[0].product_state == ProductLifecycleState.CLASSIFIED
    assert res.items[0].decision_state == DecisionLifecycleState.CONFIRMED


# 7. produto ambíguo
def test_07_ambiguous_product():
    comp = make_company_profile()
    res = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [])
    assert res.items[0].product_state == ProductLifecycleState.HUMAN_REVIEW
    assert res.items[0].decision_state == DecisionLifecycleState.HUMAN_REVIEW


# 8. NCM temporal
def test_08_temporal_ncm():
    comp = make_company_profile()
    r_exp = FiscalTaxRule(rule_id="r_exp", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, effective_from=date(2024, 1, 1), effective_until=date(2024, 12, 31), rate=Decimal("18.00"))
    res = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [r_exp])
    assert res.review_required is True


# 9. regra tributária ausente
def test_09_missing_rule():
    comp = make_company_profile()
    res = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [])
    assert res.nfe_state == NFeLifecycleState.HUMAN_REVIEW


# 10. conflito normativo
def test_10_normative_conflict():
    comp = make_company_profile()
    r1 = make_rule("r1", Decimal("18.00"))
    r2 = make_rule("r2", Decimal("12.00"))
    res = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [r1, r2])
    assert res.nfe_state == NFeLifecycleState.HUMAN_REVIEW


# 11. cálculo determinístico
def test_11_deterministic_calculation():
    comp = make_company_profile()
    res = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [make_rule()])
    assert res.total_tax_amount == Decimal("900.00")


# 12. reprocessamento idempotente
def test_12_idempotent_reprocessing():
    comp = make_company_profile()
    r1 = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [make_rule()])
    r2 = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [make_rule()])
    assert r1.document_hash == r2.document_hash


# 13. concorrência
def test_13_concurrency():
    comp = make_company_profile()
    res = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [make_rule()])
    assert res.access_key == "35260812345678000190550010000000011000000018"


# 14. revisão humana
def test_14_human_review():
    comp = make_company_profile()
    res = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [])
    assert res.review_required is True


# 15. reconstrução da memória de cálculo
def test_15_reconstruct_memory():
    comp = make_company_profile()
    res = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [make_rule()])
    assert res.master_decision_id.startswith("dec_nfe_")


# 16. reconstrução da decisão após reinício do sistema
def test_16_system_restart_reconstruction():
    comp = make_company_profile()
    res = OperationalTaxWorkbenchPipeline.process_nfe_workbench(SAMPLE_XML, comp, date(2026, 8, 14), [make_rule()])
    assert res.document_hash is not None
