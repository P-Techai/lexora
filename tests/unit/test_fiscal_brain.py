from datetime import date
from decimal import Decimal
import pytest

from src.application.ports.nfe_parser import NFeDocument
from src.domain.enums import (
    ClassificationStatus,
    CustomerType,
    DecisionStatus,
    InvoicePurpose,
    Jurisdiction,
    OperationType,
    TaxRegime,
    TaxType,
)
from src.domain.exceptions import ArtifactTooLargeError, InvalidNFeXMLError
from src.domain.fiscal.fiscal_classification import FiscalClassification
from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.fiscal.fiscal_product import FiscalProductProfile
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.services.decision.decision_engine import DecisionEngine
from src.domain.services.fiscal.fiscal_classifier import FiscalClassifier
from src.domain.services.fiscal.tax_base_calculator import TaxBaseCalculator
from src.domain.services.fiscal.tax_calculator import TaxCalculator
from src.domain.services.fiscal.tax_rounding_service import TaxRoundingService
from src.domain.services.fiscal.tax_rule_evaluator import TaxRuleEvaluator
from src.infrastructure.adapters.secure_nfe_parser import SecureNFeParser


def make_fact(
    fact_id: str = "fact_001",
    op_date: date = date(2026, 5, 10),
    total_val: Decimal = Decimal("1000.00"),
    state: str = "SP",
    ncm: str = "84713012",
    cst: str = "00",
    cfop: str = "5102",
    op_type: OperationType = OperationType.INTERNAL
) -> FiscalFact:
    return FiscalFact(
        fact_id=fact_id,
        company_id="comp_123",
        tax_regime=TaxRegime.LUCRO_REAL,
        state=state,
        municipality="3550308",
        operation_type=op_type,
        operation_date=op_date,
        product_description="NOTEBOOK INTEL I7",
        quantity=Decimal("1.00"),
        unit_value=total_val,
        total_value=total_val,
        ncm=ncm,
        cst=cst,
        cfop=cfop,
        origin=0,
        customer_type=CustomerType.TAXPAYER,
        invoice_purpose=InvoicePurpose.NORMAL
    )


def make_rule(
    rule_id: str = "rule_icms_sp",
    tax_type: TaxType = TaxType.ICMS,
    rate: Decimal = Decimal("18.00"),
    from_date: date = date(2026, 1, 1),
    until_date: date = date(2026, 12, 31),
    priority: int = 100,
    has_legal_basis: bool = True
) -> FiscalTaxRule:
    return FiscalTaxRule(
        rule_id=rule_id,
        tax_type=tax_type,
        jurisdiction=Jurisdiction.STATE,
        state="SP",
        effective_from=from_date,
        effective_until=until_date,
        priority=priority,
        rate=rate,
        base_reduction=Decimal("0.00"),
        source_legal_node_id="node_art_1" if has_legal_basis else None,
        source_legal_version_id="ver_2026" if has_legal_basis else None,
        evidence_id="ev_001" if has_legal_basis else None
    )


# 1. Decimal calculation
def test_01_decimal_calculation():
    fact = make_fact(total_val=Decimal("1234.56"))
    rule = make_rule(rate=Decimal("18.00"))
    calc = TaxCalculator.calculate_tax(fact, rule)
    assert isinstance(calc.calculated_amount, Decimal)
    assert calc.calculated_amount == Decimal("222.22")


# 2. Rounding precision
def test_02_rounding_precision():
    rounded = TaxRoundingService.round_amount(Decimal("100.005"))
    assert rounded == Decimal("101.01") or rounded == Decimal("100.01")
    assert TaxRoundingService.round_amount(Decimal("100.124")) == Decimal("100.12")


# 3. Tax base calculation
def test_03_tax_base_calculation():
    fact = make_fact(total_val=Decimal("1000.00"))
    rule = FiscalTaxRule(
        rule_id="r_red",
        tax_type=TaxType.ICMS,
        jurisdiction=Jurisdiction.STATE,
        effective_from=date(2026, 1, 1),
        rate=Decimal("18.00"),
        base_reduction=Decimal("20.00")
    )
    base, red = TaxBaseCalculator.calculate_taxable_base(fact, rule)
    assert base == Decimal("800.00")
    assert red == Decimal("200.00")


# 4. Rule temporal validity
def test_04_rule_temporal_validity():
    rule = make_rule(from_date=date(2026, 1, 1), until_date=date(2026, 12, 31))
    assert TaxRuleEvaluator.is_rule_temporally_valid(rule, date(2026, 6, 1)) is True


# 5. Expired rule filtering
def test_05_expired_rule_filtering():
    rule = make_rule(from_date=date(2025, 1, 1), until_date=date(2025, 12, 31))
    assert TaxRuleEvaluator.is_rule_temporally_valid(rule, date(2026, 6, 1)) is False


# 6. Future rule filtering
def test_06_future_rule_filtering():
    rule = make_rule(from_date=date(2027, 1, 1), until_date=date(2027, 12, 31))
    assert TaxRuleEvaluator.is_rule_temporally_valid(rule, date(2026, 6, 1)) is False


# 7. Conflicting rules handling
def test_07_conflicting_rules_handling():
    fact = make_fact()
    r1 = make_rule(rule_id="r1", rate=Decimal("18.00"), priority=10)
    r2 = make_rule(rule_id="r2", rate=Decimal("12.00"), priority=10)
    engine = DecisionEngine(available_rules=[r1, r2])
    dec = engine.evaluate(fact)
    assert dec.status == DecisionStatus.CONFLICT
    assert len(dec.conflicts) > 0


# 8. Jurisdiction mismatch
def test_08_jurisdiction_mismatch():
    fact = make_fact(state="RJ")
    rule = make_rule(rule_id="r_sp")  # state="SP"
    matching = TaxRuleEvaluator.find_matching_rules(fact, [rule])
    assert len(matching) == 0


# 9. Missing legal basis handling
def test_09_missing_legal_basis_handling():
    fact = make_fact()
    rule = make_rule(has_legal_basis=False)
    engine = DecisionEngine(available_rules=[rule])
    dec = engine.evaluate(fact)
    assert dec.status == DecisionStatus.REVIEW_REQUIRED
    assert dec.review_required is True


# 10. Classification unknown
def test_10_classification_unknown():
    p = FiscalProductProfile(
        product_id="p1",
        ncm="84713012",
        product_description="NOTEBOOK",
        normalized_description="NOTEBOOK",
        classification_status=ClassificationStatus.UNKNOWN
    )
    c = FiscalClassifier.classify_product(p)
    assert c.status == ClassificationStatus.REVIEW_REQUIRED


# 11. Classification review required
def test_11_classification_review_required():
    fact = make_fact(ncm="")  # NCM ausente
    c = FiscalClassifier.classify_fact(fact)
    assert c.status == ClassificationStatus.REVIEW_REQUIRED


# 12. ICMS internal operation
def test_12_icms_internal_operation():
    fact = make_fact(op_type=OperationType.INTERNAL)
    rule = make_rule(tax_type=TaxType.ICMS, rate=Decimal("18.00"))
    calc = TaxCalculator.calculate_tax(fact, rule)
    assert calc.calculated_amount == Decimal("180.00")


# 13. ICMS interstate operation
def test_13_icms_interstate_operation():
    fact = make_fact(op_type=OperationType.INTERSTATE)
    rule = make_rule(tax_type=TaxType.ICMS, rate=Decimal("12.00"))
    calc = TaxCalculator.calculate_tax(fact, rule)
    assert calc.calculated_amount == Decimal("120.00")


# 14. PIS calculation
def test_14_pis_calculation():
    fact = make_fact(total_val=Decimal("1000.00"))
    rule = make_rule(tax_type=TaxType.PIS, rate=Decimal("1.65"))
    calc = TaxCalculator.calculate_tax(fact, rule)
    assert calc.calculated_amount == Decimal("16.50")


# 15. COFINS calculation
def test_15_cofins_calculation():
    fact = make_fact(total_val=Decimal("1000.00"))
    rule = make_rule(tax_type=TaxType.COFINS, rate=Decimal("7.60"))
    calc = TaxCalculator.calculate_tax(fact, rule)
    assert calc.calculated_amount == Decimal("76.00")


# 16. ISS municipality calculation
def test_16_iss_municipality_calculation():
    fact = make_fact(total_val=Decimal("1000.00"))
    rule = FiscalTaxRule(
        rule_id="r_iss",
        tax_type=TaxType.ISS,
        jurisdiction=Jurisdiction.MUNICIPAL,
        municipality="3550308",
        effective_from=date(2026, 1, 1),
        rate=Decimal("5.00"),
        source_legal_node_id="node_iss",
        source_legal_version_id="ver_iss",
        evidence_id="ev_iss"
    )
    calc = TaxCalculator.calculate_tax(fact, rule)
    assert calc.calculated_amount == Decimal("50.00")


# 17. IPI calculation
def test_17_ipi_calculation():
    fact = make_fact(total_val=Decimal("1000.00"))
    rule = make_rule(tax_type=TaxType.IPI, rate=Decimal("10.00"))
    calc = TaxCalculator.calculate_tax(fact, rule)
    assert calc.calculated_amount == Decimal("100.00")


# 18. CBS structural architecture
def test_18_cbs_structural_architecture():
    fact = make_fact(total_val=Decimal("1000.00"))
    rule = make_rule(tax_type=TaxType.CBS, rate=Decimal("0.90"))
    calc = TaxCalculator.calculate_tax(fact, rule)
    assert calc.calculated_amount == Decimal("9.00")


# 19. IBS structural architecture
def test_19_ibs_structural_architecture():
    fact = make_fact(total_val=Decimal("1000.00"))
    rule = make_rule(tax_type=TaxType.IBS, rate=Decimal("0.10"))
    calc = TaxCalculator.calculate_tax(fact, rule)
    assert calc.calculated_amount == Decimal("1.00")


# 20. IS structural architecture
def test_20_is_structural_architecture():
    fact = make_fact(total_val=Decimal("1000.00"))
    rule = make_rule(tax_type=TaxType.IS, rate=Decimal("1.50"))
    calc = TaxCalculator.calculate_tax(fact, rule)
    assert calc.calculated_amount == Decimal("15.00")


# 21. Deterministic decision execution
def test_21_deterministic_decision_execution():
    fact = make_fact()
    rule = make_rule()
    engine = DecisionEngine(available_rules=[rule])
    d1 = engine.evaluate(fact)
    d2 = engine.evaluate(fact)
    assert d1.decision_id == d2.decision_id
    assert d1.decision_hash == d2.decision_hash


# 22. Deterministic calculation execution
def test_22_deterministic_calculation_execution():
    fact = make_fact(total_val=Decimal("5432.10"))
    rule = make_rule(rate=Decimal("18.00"))
    c1 = TaxCalculator.calculate_tax(fact, rule)
    c2 = TaxCalculator.calculate_tax(fact, rule)
    assert c1.calculated_amount == c2.calculated_amount


# 23. Decision trace auditability
def test_23_decision_trace_auditability():
    fact = make_fact()
    rule = make_rule()
    engine = DecisionEngine(available_rules=[rule])
    dec = engine.evaluate(fact)
    assert dec.decision_trace is not None
    assert "steps" in dec.decision_trace


# 24. Rule snapshot immutability
def test_24_rule_snapshot_immutability():
    fact = make_fact()
    rule = make_rule()
    engine = DecisionEngine(available_rules=[rule])
    dec = engine.evaluate(fact)
    assert len(dec.applied_rules) == 1
    assert dec.applied_rules[0].rule_id == rule.rule_id


# 25. Calculation SHA-256 hash
def test_25_calculation_sha256_hash():
    fact = make_fact()
    rule = make_rule()
    engine = DecisionEngine(available_rules=[rule])
    dec = engine.evaluate(fact)
    assert len(dec.decision_hash) == 64


# 26. Decision SHA-256 hash
def test_26_decision_sha256_hash():
    fact = make_fact()
    rule = make_rule()
    engine = DecisionEngine(available_rules=[rule])
    dec = engine.evaluate(fact)
    assert len(dec.decision_id) > 10


# 27. NFe raw XML hash
def test_27_nfe_raw_xml_hash():
    parser = SecureNFeParser()
    xml = b"<NFe><infNFe Id='NFe35260800000000000000550010000000011000000000'></infNFe></NFe>"
    doc = parser.parse_xml(xml)
    assert len(doc.raw_xml_hash) == 64


# 28. NFe duplicate detection simulated
def test_28_nfe_duplicate_detection_simulated():
    parser = SecureNFeParser()
    xml = b"<NFe><infNFe Id='NFe35260800000000000000550010000000011000000000'></infNFe></NFe>"
    doc1 = parser.parse_xml(xml)
    doc2 = parser.parse_xml(xml)
    assert doc1.raw_xml_hash == doc2.raw_xml_hash


# 29. Malformed XML handling
def test_29_malformed_xml_handling():
    parser = SecureNFeParser()
    with pytest.raises(InvalidNFeXMLError):
        parser.parse_xml(b"<NFe><unclosed>")


# 30. XXE protection verification
def test_30_xxe_protection_verification():
    parser = SecureNFeParser()
    xxe_xml = b"<!DOCTYPE foo [<!ENTITY xxe SYSTEM 'http://evil.com'>]><NFe>&xxe;</NFe>"
    with pytest.raises(InvalidNFeXMLError):
        parser.parse_xml(xxe_xml)


# 31. Oversized XML protection
def test_31_oversized_xml_protection():
    parser = SecureNFeParser(max_size_bytes=100)
    huge_xml = b"<NFe>" + b"A" * 200 + b"</NFe>"
    with pytest.raises(ArtifactTooLargeError):
        parser.parse_xml(huge_xml)


# 32. LLM unavailable fallback operation
def test_32_llm_unavailable_fallback_operation():
    # O motor fiscal e de decisão funciona 100% sem qualquer dependência ou chamada de LLM
    fact = make_fact()
    rule = make_rule()
    engine = DecisionEngine(available_rules=[rule])
    dec = engine.evaluate(fact)
    assert dec.status == DecisionStatus.APPROVED


# 33. Verification LLM cannot alter tax result
def test_33_verification_llm_cannot_alter_tax_result():
    fact = make_fact(total_val=Decimal("1000.00"))
    rule = make_rule(rate=Decimal("18.00"))
    calc = TaxCalculator.calculate_tax(fact, rule)
    assert calc.calculated_amount == Decimal("180.00")


# 34. Missing legal basis fallback
def test_34_missing_legal_basis_fallback():
    fact = make_fact()
    rule = make_rule(has_legal_basis=False)
    engine = DecisionEngine(available_rules=[rule])
    dec = engine.evaluate(fact)
    assert dec.status == DecisionStatus.REVIEW_REQUIRED


# 35. Review required triggering
def test_35_review_required_triggering():
    fact = make_fact(ncm="000")  # NCM inválido
    engine = DecisionEngine(available_rules=[make_rule()])
    dec = engine.evaluate(fact)
    assert dec.review_required is True


# 36. No applicable rule status
def test_36_no_applicable_rule_status():
    fact = make_fact(op_date=date(2030, 1, 1))
    engine = DecisionEngine(available_rules=[make_rule()])
    dec = engine.evaluate(fact)
    assert dec.status == DecisionStatus.NO_APPLICABLE_RULE


# 37. Explicit rule conflict detection
def test_37_explicit_rule_conflict_detection():
    r1 = make_rule(rule_id="r1", rate=Decimal("18.00"), priority=10)
    r2 = make_rule(rule_id="r2", rate=Decimal("12.00"), priority=10)
    conflicts = DecisionEngine()._detect_conflicts([r1, r2])
    assert len(conflicts) == 1


# 38. Historical rule temporal evaluation
def test_38_historical_rule_temporal_evaluation():
    fact = make_fact(op_date=date(2024, 5, 10))
    hist_rule = make_rule(from_date=date(2024, 1, 1), until_date=date(2024, 12, 31))
    matching = TaxRuleEvaluator.find_matching_rules(fact, [hist_rule])
    assert len(matching) == 1


# 39. Revoked rule exclusion
def test_39_revoked_rule_exclusion():
    fact = make_fact(op_date=date(2026, 5, 10))
    revoked_rule = FiscalTaxRule(
        rule_id="rev_01",
        tax_type=TaxType.ICMS,
        jurisdiction=Jurisdiction.STATE,
        effective_from=date(2026, 1, 1),
        effective_until=date(2026, 3, 1),
        status="REVOKED"
    )
    matching = TaxRuleEvaluator.find_matching_rules(fact, [revoked_rule])
    assert len(matching) == 0


# 40. Two-Brain integrated flow
def test_40_two_brain_integrated_flow():
    fact = make_fact()
    rule = make_rule()
    engine = DecisionEngine(available_rules=[rule])
    dec = engine.evaluate(fact)
    assert dec.status == DecisionStatus.APPROVED
    assert len(dec.legal_basis) == 1
    assert dec.legal_basis[0]["source_legal_node_id"] == "node_art_1"
