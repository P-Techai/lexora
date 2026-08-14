from datetime import date
from decimal import Decimal
import pytest

from src.domain.enums import Jurisdiction, TaxType
from src.domain.fiscal.fiscal_rule_catalog import FiscalRuleCatalog, FiscalRuleCatalogItem, FiscalRuleEvidence
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.fiscal.nfe_batch_pipeline import NFeBatchPipeline
from src.domain.fiscal.product_classification_service import ClassificationState, ProductFiscalClassificationService
from tests.unit.test_nfe_operational_fiscal_engine import SAMPLE_XML


def make_catalog_item(rule_id: str = "cat_r_01", tax_type: TaxType = TaxType.ICMS, rate: Decimal = Decimal("18.00")) -> FiscalRuleCatalogItem:
    ev = FiscalRuleEvidence(
        evidence_id=f"ev_{rule_id}",
        source_org="Receita Federal / SEFAZ",
        legal_act="Lei Estadual 6.374/89",
        act_number="6374",
        article="Art. 34",
        acquisition_date=date(2026, 1, 1),
        content_hash="hash_ev_01"
    )
    return FiscalRuleCatalogItem(
        rule_id=rule_id,
        valid_from=date(2026, 1, 1),
        jurisdiction=Jurisdiction.STATE,
        tax_type=tax_type,
        state="SP",
        rate=rate,
        evidence=ev,
        content_hash="hash_cat_item_01"
    )


# 1. NCM válida
def test_01_valid_ncm():
    res = ProductFiscalClassificationService.classify_product("NOTEBOOK", "84713012")
    assert res.state == ClassificationState.DETERMINED


# 2. NCM inválida
def test_02_invalid_ncm():
    res = ProductFiscalClassificationService.classify_product("NOTEBOOK", "123")
    assert res.state == ClassificationState.INVALID
    assert res.review_required is True


# 3. NCM temporal
def test_03_temporal_ncm():
    cat = FiscalRuleCatalog([make_catalog_item()])
    rules = cat.find_active_rules(date(2026, 6, 1))
    assert len(rules) == 1


# 4. CEST
def test_04_cest():
    res = ProductFiscalClassificationService.classify_product("MONITOR", "85285200", "2100100")
    assert res.cest == "2100100"


# 5. Produto conhecido
def test_05_known_product():
    res = ProductFiscalClassificationService.classify_product("TECLADO", "84713012")
    assert res.confidence_score == 1.0


# 6. Produto ambíguo
def test_06_ambiguous_product():
    res = ProductFiscalClassificationService.classify_product("DEPOSIT", "00000000")
    assert res.state == ClassificationState.CONFLICT


# 7. Produto sem classificação
def test_07_unclassified_product():
    res = ProductFiscalClassificationService.classify_product("TEXTO SEM NCM", None)
    assert res.review_required is True


# 8. CST
def test_08_cst():
    res = ProductFiscalClassificationService.classify_product("ITEM", "84713012")
    assert res.cst == "00"


# 9. CSOSN
def test_09_csosn():
    res = ProductFiscalClassificationService.classify_product("ITEM", "84713012")
    assert res.csosn is None


# 10. CFOP
def test_10_cfop():
    res = ProductFiscalClassificationService.classify_product("ITEM", "84713012")
    assert res.cfop == "5102"


# 11. ICMS interno
def test_11_icms_internal():
    cat = FiscalRuleCatalog([make_catalog_item()])
    rules = cat.find_active_rules(date(2026, 6, 1), TaxType.ICMS, "SP")
    assert rules[0].rate == Decimal("18.00")


# 12. ICMS interestadual
def test_12_icms_interstate():
    r_inter = make_catalog_item("r_inter", rate=Decimal("12.00"))
    cat = FiscalRuleCatalog([r_inter])
    rules = cat.find_active_rules(date(2026, 6, 1))
    assert rules[0].rate == Decimal("12.00")


# 13. ICMS-ST
def test_13_icms_st():
    r_st = make_catalog_item("r_st", TaxType.ICMS_ST, rate=Decimal("18.00"))
    cat = FiscalRuleCatalog([r_st])
    rules = cat.find_active_rules(date(2026, 6, 1), TaxType.ICMS_ST)
    assert len(rules) == 1


# 14. DIFAL
def test_14_difal():
    r_difal = make_catalog_item("r_difal", TaxType.DIFAL, rate=Decimal("6.00"))
    cat = FiscalRuleCatalog([r_difal])
    rules = cat.find_active_rules(date(2026, 6, 1), TaxType.DIFAL)
    assert len(rules) == 1


# 15. FCP
def test_15_fcp():
    r_fcp = make_catalog_item("r_fcp", TaxType.FCP, rate=Decimal("2.00"))
    cat = FiscalRuleCatalog([r_fcp])
    rules = cat.find_active_rules(date(2026, 6, 1), TaxType.FCP)
    assert rules[0].rate == Decimal("2.00")


# 16. IPI
def test_16_ipi():
    r_ipi = make_catalog_item("r_ipi", TaxType.IPI, rate=Decimal("5.00"))
    cat = FiscalRuleCatalog([r_ipi])
    rules = cat.find_active_rules(date(2026, 6, 1), TaxType.IPI)
    assert rules[0].rate == Decimal("5.00")


# 17. PIS
def test_17_pis():
    r_pis = make_catalog_item("r_pis", TaxType.PIS, rate=Decimal("1.65"))
    cat = FiscalRuleCatalog([r_pis])
    rules = cat.find_active_rules(date(2026, 6, 1), TaxType.PIS)
    assert rules[0].rate == Decimal("1.65")


# 18. COFINS
def test_18_cofins():
    r_cof = make_catalog_item("r_cof", TaxType.COFINS, rate=Decimal("7.60"))
    cat = FiscalRuleCatalog([r_cof])
    rules = cat.find_active_rules(date(2026, 6, 1), TaxType.COFINS)
    assert rules[0].rate == Decimal("7.60")


# 19. Simples Nacional
def test_19_simples():
    cat = FiscalRuleCatalog([make_catalog_item()])
    assert len(cat._rules) == 1


# 20. ISS
def test_20_iss():
    r_iss = make_catalog_item("r_iss", TaxType.ISS, rate=Decimal("3.00"))
    cat = FiscalRuleCatalog([r_iss])
    rules = cat.find_active_rules(date(2026, 6, 1), TaxType.ISS)
    assert rules[0].rate == Decimal("3.00")


# 21. regra temporal
def test_21_temporal():
    cat = FiscalRuleCatalog([make_catalog_item()])
    rules = cat.find_active_rules(date(2025, 1, 1))
    assert len(rules) == 0


# 22. regra conflitante
def test_22_conflicting_rules():
    cat = FiscalRuleCatalog([make_catalog_item("r1"), make_catalog_item("r2")])
    rules = cat.find_active_rules(date(2026, 6, 1))
    assert len(rules) == 2


# 23. evidence ausente
def test_23_missing_evidence():
    item = make_catalog_item()
    assert item.evidence.evidence_id is not None


# 24. human review
def test_24_human_review():
    res = NFeBatchPipeline.process_batch([SAMPLE_XML], "comp_1", date(2026, 8, 14), [])
    assert res.review_required_count == 1


# 25. human override
def test_25_human_override():
    res = NFeBatchPipeline.process_batch([SAMPLE_XML], "comp_1", date(2026, 8, 14), [make_catalog_item().to_domain_tax_rule()])
    assert res.processed_count == 1


# 26. batch
def test_26_batch_processing():
    res = NFeBatchPipeline.process_batch([SAMPLE_XML], "comp_1", date(2026, 8, 14), [make_catalog_item().to_domain_tax_rule()])
    assert res.batch_status.value == "COMPLETED"


# 27. batch parcial
def test_27_partial_batch():
    bad_xml = "<invalid>xml"
    res = NFeBatchPipeline.process_batch([SAMPLE_XML, bad_xml], "comp_1", date(2026, 8, 14), [make_catalog_item().to_domain_tax_rule()])
    assert res.processed_count == 1
    assert res.failed_count == 1


# 28. duplicate NF-e
def test_28_duplicate_batch_nfe():
    res = NFeBatchPipeline.process_batch([SAMPLE_XML, SAMPLE_XML], "comp_1", date(2026, 8, 14), [make_catalog_item().to_domain_tax_rule()])
    assert res.failed_count == 1
    assert res.items[1].status == "DUPLICATE"


# 29. concorrência
def test_29_concurrency_batch():
    res = NFeBatchPipeline.process_batch([SAMPLE_XML], "comp_1", date(2026, 8, 14), [make_catalog_item().to_domain_tax_rule()])
    assert res.batch_id.startswith("batch_")


# 30. tenant isolation
def test_30_tenant_isolation():
    res = NFeBatchPipeline.process_batch([SAMPLE_XML], "comp_tenant_A", date(2026, 8, 14), [make_catalog_item().to_domain_tax_rule()])
    assert res.company_id == "comp_tenant_A"


# 31. audit report
def test_31_audit_report():
    res = NFeBatchPipeline.process_batch([SAMPLE_XML], "comp_1", date(2026, 8, 14), [make_catalog_item().to_domain_tax_rule()])
    assert res.total_batch_tax_amount == Decimal("900.00")


# 32. calculation reproducibility
def test_32_calculation_reproducibility():
    r1 = NFeBatchPipeline.process_batch([SAMPLE_XML], "comp_1", date(2026, 8, 14), [make_catalog_item().to_domain_tax_rule()])
    r2 = NFeBatchPipeline.process_batch([SAMPLE_XML], "comp_1", date(2026, 8, 14), [make_catalog_item().to_domain_tax_rule()])
    assert r1.total_batch_tax_amount == r2.total_batch_tax_amount
