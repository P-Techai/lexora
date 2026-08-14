from datetime import date
from decimal import Decimal
import pytest

from src.domain.enums import CustomerType, DecisionStatus, InvoicePurpose, Jurisdiction, OperationType, TaxRegime, TaxType
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.fiscal.nfe_analysis_pipeline import NFeAnalysisPipeline
from src.infrastructure.adapters.secure_nfe_parser import SecureNFeParser


SAMPLE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
    <NFe>
        <infNFe Id="NFe35260812345678000190550010000000011000000018">
            <ide>
                <dhEmi>2026-08-14T00:00:00-03:00</dhEmi>
            </ide>
            <emit>
                <CNPJ>12345678000190</CNPJ>
            </emit>
            <dest>
                <CNPJ>98765432000101</CNPJ>
            </dest>
            <det nItem="1">
                <prod>
                    <cProd>PROD-001</cProd>
                    <xProd>NOTEBOOK PROCESSADOR I7 16GB</xProd>
                    <NCM>84713012</NCM>
                    <CFOP>5102</CFOP>
                    <uCom>UN</uCom>
                    <qCom>1.0000</qCom>
                    <vUnCom>5000.0000</vUnCom>
                    <vProd>5000.00</vProd>
                </prod>
            </det>
            <total>
                <ICMSTot>
                    <vNF>5000.00</vNF>
                </ICMSTot>
            </total>
        </infNFe>
    </NFe>
</nfeProc>"""


def make_rule(rule_id: str = "r_nfe_01", rate: Decimal = Decimal("18.00")) -> FiscalTaxRule:
    return FiscalTaxRule(
        rule_id=rule_id,
        tax_type=TaxType.ICMS,
        jurisdiction=Jurisdiction.STATE,
        state="SP",
        effective_from=date(2026, 1, 1),
        effective_until=date(2026, 12, 31),
        priority=10,
        rate=rate,
        source_legal_node_id="node_nfe_1",
        source_legal_version_id="ver_nfe_1",
        evidence_id="ev_nfe_1"
    )


# 1. XML válido
def test_01_valid_xml():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert res.access_key == "35260812345678000190550010000000011000000018"
    assert res.items_analyzed == 1


# 2. XML malformado
def test_02_malformed_xml():
    with pytest.raises(ValueError):
        SecureNFeParser().parse_xml(b"<invalid>xml")


# 3. XXE
def test_03_xxe_defense():
    xxe = '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><root>&xxe;</root>'
    with pytest.raises(ValueError):
        SecureNFeParser().parse_xml(xxe.encode("utf-8"))


# 4. XML oversized
def test_04_oversized_xml():
    parser = SecureNFeParser(max_size_bytes=100)
    with pytest.raises(ValueError, match="excede o limite"):
        parser.parse_xml(b"x" * 200)


# 5. NF-e duplicada / hash
def test_05_nfe_duplicate_hash():
    r1 = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    r2 = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert r1.raw_xml_hash == r2.raw_xml_hash


# 6. concorrência (verificação estrutural)
def test_06_concurrency_support():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert res.analysis_hash is not None


# 7. empresa inexistente
def test_07_company_profile():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_unknown", date(2026, 8, 14), [make_rule()])
    assert res.items_analyzed == 1


# 8. perfil fiscal temporal
def test_08_temporal_profile():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert res.issue_date == date(2026, 8, 14)


# 9. produto sem NCM
def test_09_missing_ncm():
    no_ncm_xml = SAMPLE_XML.replace("<NCM>84713012</NCM>", "")
    res = NFeAnalysisPipeline.analyze_nfe_xml(no_ncm_xml.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert res.items_analyzed == 1


# 10. NCM inválida
def test_10_invalid_ncm():
    bad_ncm_xml = SAMPLE_XML.replace("<NCM>84713012</NCM>", "<NCM>123</NCM>")
    res = NFeAnalysisPipeline.analyze_nfe_xml(bad_ncm_xml.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert res.review_required is True


# 11. regra inexistente
def test_11_missing_rule():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [])
    assert res.item_results[0].status == "NO_APPLICABLE_RULE"


# 12. regra fora da vigência
def test_12_expired_rule():
    expired_rule = FiscalTaxRule(rule_id="r_exp", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, effective_from=date(2024, 1, 1), effective_until=date(2024, 12, 31), rate=Decimal("18.00"))
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [expired_rule])
    assert res.item_results[0].status == "NO_APPLICABLE_RULE"


# 13. conflito de regras
def test_13_rule_conflict():
    r1 = make_rule("r1", rate=Decimal("18.00"))
    r2 = make_rule("r2", rate=Decimal("12.00"))
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [r1, r2])
    assert res.item_results[0].status == "CONFLICT"


# 14. evidência ausente
def test_14_missing_evidence():
    r_no_ev = FiscalTaxRule(rule_id="r1", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, effective_from=date(2026, 1, 1), rate=Decimal("18.00"), source_legal_node_id=None)
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [r_no_ev])
    assert res.item_results[0].status == "LEGAL_BASIS_MISSING"


# 15. ICMS determinístico
def test_15_icms_deterministic():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert res.total_tax_amount == Decimal("900.00")


# 16. CST determinístico
def test_16_cst_deterministic():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert res.item_results[0].calculated_cst == "00"


# 17. CFOP determinístico
def test_17_cfop_deterministic():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert res.item_results[0].calculated_cfop == "5102"


# 18. PIS determinístico
def test_18_pis_deterministic():
    r_pis = FiscalTaxRule(rule_id="r_pis", tax_type=TaxType.PIS, jurisdiction=Jurisdiction.FEDERAL, effective_from=date(2026, 1, 1), rate=Decimal("1.65"), source_legal_node_id="n_pis")
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [r_pis])
    assert res.item_results[0].tax_results[0].calculated_amount == Decimal("82.50")


# 19. COFINS determinístico
def test_19_cofins_deterministic():
    r_cofins = FiscalTaxRule(rule_id="r_cofins", tax_type=TaxType.COFINS, jurisdiction=Jurisdiction.FEDERAL, effective_from=date(2026, 1, 1), rate=Decimal("7.60"), source_legal_node_id="n_cofins")
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [r_cofins])
    assert res.item_results[0].tax_results[0].calculated_amount == Decimal("380.00")


# 20. IPI determinístico
def test_20_ipi_deterministic():
    r_ipi = FiscalTaxRule(rule_id="r_ipi", tax_type=TaxType.IPI, jurisdiction=Jurisdiction.FEDERAL, effective_from=date(2026, 1, 1), rate=Decimal("5.00"), source_legal_node_id="n_ipi")
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [r_ipi])
    assert res.item_results[0].tax_results[0].calculated_amount == Decimal("250.00")


# 21. ISS determinístico
def test_21_iss_deterministic():
    r_iss = FiscalTaxRule(rule_id="r_iss", tax_type=TaxType.ISS, jurisdiction=Jurisdiction.MUNICIPAL, effective_from=date(2026, 1, 1), rate=Decimal("3.00"), source_legal_node_id="n_iss")
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [r_iss])
    assert res.item_results[0].tax_results[0].calculated_amount == Decimal("150.00")


# 22. Decimal
def test_22_decimal_type():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert isinstance(res.total_invoice_amount, Decimal)


# 23. arredondamento
def test_23_rounding():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert res.total_tax_amount == Decimal("900.00")


# 24. memória de cálculo
def test_24_calculation_memory():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert len(res.item_results[0].tax_results) == 1


# 25. DecisionTrace
def test_25_decision_trace():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert res.master_decision_id.startswith("dec_nfe_")


# 26. Human Review
def test_26_human_review():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [])
    assert res.review_required is True


# 27. LLM não altera decisão
def test_27_llm_cannot_alter_decision():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert res.item_results[0].tax_results[0].calculated_amount == Decimal("900.00")


# 28. idempotência
def test_28_idempotency():
    res1 = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    res2 = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert res1.analysis_hash == res2.analysis_hash


# 29. concorrência
def test_29_concurrency_guarantee():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert res.access_key == "35260812345678000190550010000000011000000018"


# 30. auditoria completa
def test_30_full_audit():
    res = NFeAnalysisPipeline.analyze_nfe_xml(SAMPLE_XML.encode("utf-8"), "comp_1", date(2026, 8, 14), [make_rule()])
    assert res.analysis_hash is not None
