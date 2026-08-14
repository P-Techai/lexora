from datetime import date
from decimal import Decimal
import pytest

from src.domain.enums import Jurisdiction, TaxType
from src.domain.fiscal.fiscal_rule_catalog import FiscalRuleCatalog, FiscalRuleCatalogItem, FiscalRuleEvidence
from src.domain.fiscal.nfe_batch_pipeline import NFeBatchPipeline
from src.domain.fiscal.product_classification_service import ClassificationState, ProductFiscalClassificationService
from tests.unit.test_nfe_operational_fiscal_engine import SAMPLE_XML
from tests.unit.test_real_fiscal_knowledge_batch import make_catalog_item


def test_golden_08_01_classified_product():
    """GOLDEN-08.01: Produto corretamente classificado."""
    res = ProductFiscalClassificationService.classify_product("NOTEBOOK PROCESSADOR I7", "84713012")
    assert res.state == ClassificationState.DETERMINED
    assert res.ncm == "84713012"
    assert res.cst == "00"
    assert res.cfop == "5102"


def test_golden_08_02_temporal_ncm():
    """GOLDEN-08.02: NCM temporal vigente em 2026."""
    item = make_catalog_item("r_ncm_temp")
    cat = FiscalRuleCatalog([item])
    rules_2026 = cat.find_active_rules(date(2026, 6, 15))
    rules_2024 = cat.find_active_rules(date(2024, 6, 15))
    assert len(rules_2026) == 1
    assert len(rules_2024) == 0


def test_golden_08_03_cest():
    """GOLDEN-08.03: CEST vinculado a NCM e ST."""
    res = ProductFiscalClassificationService.classify_product("MONITOR LCD 27", "85285200", "2100100")
    assert res.cest == "2100100"


def test_golden_08_04_icms_st():
    """GOLDEN-08.04: ICMS-ST com MVA e alíquota estaduais."""
    r_st = make_catalog_item("r_st", TaxType.ICMS_ST, rate=Decimal("18.00"))
    res = NFeBatchPipeline.process_batch([SAMPLE_XML], "comp_g8_4", date(2026, 8, 14), [r_st.to_domain_tax_rule()])
    assert res.batch_status.value == "COMPLETED"
    assert res.total_batch_tax_amount == Decimal("900.00")


def test_golden_08_05_difal():
    """GOLDEN-08.05: DIFAL em operação interestadual."""
    r_difal = make_catalog_item("r_difal", TaxType.DIFAL, rate=Decimal("6.00"))
    res = NFeBatchPipeline.process_batch([SAMPLE_XML], "comp_g8_5", date(2026, 8, 14), [r_difal.to_domain_tax_rule()])
    assert res.total_batch_tax_amount == Decimal("300.00")


def test_golden_08_06_fcp():
    """GOLDEN-08.06: FCP isolado de 2%."""
    r_fcp = make_catalog_item("r_fcp", TaxType.FCP, rate=Decimal("2.00"))
    res = NFeBatchPipeline.process_batch([SAMPLE_XML], "comp_g8_6", date(2026, 8, 14), [r_fcp.to_domain_tax_rule()])
    assert res.total_batch_tax_amount == Decimal("100.00")


def test_golden_08_07_simples_nacional():
    """GOLDEN-08.07: Simples Nacional CRT/CSOSN."""
    res = ProductFiscalClassificationService.classify_product("ITEM SIMPLES", "84713012")
    assert res.state == ClassificationState.DETERMINED


def test_golden_08_08_iss_municipal():
    """GOLDEN-08.08: ISS municipal de 3%."""
    r_iss = make_catalog_item("r_iss", TaxType.ISS, rate=Decimal("3.00"))
    res = NFeBatchPipeline.process_batch([SAMPLE_XML], "comp_g8_8", date(2026, 8, 14), [r_iss.to_domain_tax_rule()])
    assert res.total_batch_tax_amount == Decimal("150.00")


def test_golden_08_09_ambiguous_product():
    """GOLDEN-08.09: Produto ambíguo exigindo REQUIRES_HUMAN_REVIEW."""
    res = NFeBatchPipeline.process_batch([SAMPLE_XML], "comp_g8_9", date(2026, 8, 14), [])
    assert res.review_required_count == 1
    assert res.batch_status.value == "REQUIRES_REVIEW"


def test_golden_08_10_conflicting_rules():
    """GOLDEN-08.10: Regras conflitantes exigindo REQUIRES_HUMAN_REVIEW."""
    r1 = make_catalog_item("r1", rate=Decimal("18.00")).to_domain_tax_rule()
    r2 = make_catalog_item("r2", rate=Decimal("12.00")).to_domain_tax_rule()

    res = NFeBatchPipeline.process_batch([SAMPLE_XML], "comp_g8_10", date(2026, 8, 14), [r1, r2])
    assert res.review_required_count == 1
    assert res.batch_status.value == "REQUIRES_REVIEW"
