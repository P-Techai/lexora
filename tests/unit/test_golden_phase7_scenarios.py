from datetime import date
from decimal import Decimal
import pytest

from src.domain.enums import CustomerType, DecisionStatus, InvoicePurpose, Jurisdiction, OperationType, TaxRegime, TaxType
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.fiscal.nfe_analysis_pipeline import NFeAnalysisPipeline
from tests.unit.test_nfe_operational_fiscal_engine import SAMPLE_XML


def test_golden_01_internal_operation():
    """GOLDEN-01: Operação interna com ICMS, PIS e COFINS."""
    r_icms = FiscalTaxRule(rule_id="r_icms_01", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, state="SP", effective_from=date(2026, 1, 1), rate=Decimal("18.00"), source_legal_node_id="n1", evidence_id="e1")
    r_pis = FiscalTaxRule(rule_id="r_pis_01", tax_type=TaxType.PIS, jurisdiction=Jurisdiction.FEDERAL, effective_from=date(2026, 1, 1), rate=Decimal("1.65"), source_legal_node_id="n2", evidence_id="e2")
    r_cofins = FiscalTaxRule(rule_id="r_cofins_01", tax_type=TaxType.COFINS, jurisdiction=Jurisdiction.FEDERAL, effective_from=date(2026, 1, 1), rate=Decimal("7.60"), source_legal_node_id="n3", evidence_id="e3")

    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_gold_1", date(2026, 8, 14), [r_icms, r_pis, r_cofins])

    assert res.review_required is False
    assert len(res.item_results[0].tax_results) == 3
    assert res.total_tax_amount == Decimal("1362.50")


def test_golden_02_interstate_operation():
    """GOLDEN-02: Operação interestadual com ICMS, DIFAL e FCP."""
    r_icms = FiscalTaxRule(rule_id="r_icms_inter", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, state="SP", effective_from=date(2026, 1, 1), rate=Decimal("12.00"), source_legal_node_id="n1", evidence_id="e1")
    r_fcp = FiscalTaxRule(rule_id="r_fcp_inter", tax_type=TaxType.FCP, jurisdiction=Jurisdiction.STATE, state="SP", effective_from=date(2026, 1, 1), rate=Decimal("2.00"), source_legal_node_id="n4", evidence_id="e4")

    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_gold_2", date(2026, 8, 14), [r_icms, r_fcp])

    assert res.review_required is False
    assert len(res.item_results[0].tax_results) == 2
    assert res.total_tax_amount == Decimal("700.00")


def test_golden_03_temporal_rule():
    """GOLDEN-03: Regra temporal de 2024 aplicada a operação de 2024 e não regra de 2025."""
    r_2024 = FiscalTaxRule(rule_id="r_2024", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, state="SP", effective_from=date(2024, 1, 1), effective_until=date(2024, 12, 31), rate=Decimal("12.00"), source_legal_node_id="n2024", evidence_id="e2024")
    r_2025 = FiscalTaxRule(rule_id="r_2025", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, state="SP", effective_from=date(2025, 1, 1), effective_until=date(2026, 12, 31), rate=Decimal("18.00"), source_legal_node_id="n2025", evidence_id="e2025")

    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_gold_3", date(2024, 6, 15), [r_2024, r_2025])

    assert res.review_required is False
    assert len(res.item_results[0].tax_results) == 1
    assert res.item_results[0].tax_results[0].rate == Decimal("12.00")


def test_golden_04_ambiguous_item_human_review():
    """GOLDEN-04: Caso ambíguo com ausência de regra aplicável exigindo HUMAN REVIEW."""
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_gold_4", date(2026, 8, 14), [])

    assert res.review_required is True
    assert res.item_results[0].status == "NO_APPLICABLE_RULE"


def test_golden_05_rule_conflict():
    """GOLDEN-05: Conflito normativo de duas regras com mesma prioridade exigindo HUMAN REVIEW."""
    r1 = FiscalTaxRule(rule_id="r1", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, state="SP", effective_from=date(2026, 1, 1), priority=10, rate=Decimal("18.00"), source_legal_node_id="n1", evidence_id="e1")
    r2 = FiscalTaxRule(rule_id="r2", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, state="SP", effective_from=date(2026, 1, 1), priority=10, rate=Decimal("12.00"), source_legal_node_id="n2", evidence_id="e2")

    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_gold_5", date(2026, 8, 14), [r1, r2])

    assert res.review_required is True
    assert res.item_results[0].status == "CONFLICT"
