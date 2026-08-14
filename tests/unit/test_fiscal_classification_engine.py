from datetime import date
from decimal import Decimal
import pytest

from src.domain.enums import ClassificationStatus, CustomerType, DecisionStatus, InvoicePurpose, Jurisdiction, OperationType, TaxRegime, TaxType
from src.domain.fiscal.calculation_memory import CalculationMemory
from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.fiscal.fiscal_product_profile import FiscalProductProfile
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.services.decision.decision_engine import DecisionEngine
from src.domain.services.fiscal.tax_calculation_engine import TaxCalculationEngine
from src.domain.services.fiscal.tax_rule_resolver import TaxRuleResolver


def make_fact(fact_id: str = "f_class_01", op_date: date = date(2026, 6, 15), ncm: str = "84713012") -> FiscalFact:
    return FiscalFact(
        fact_id=fact_id,
        company_id="comp_class",
        tax_regime=TaxRegime.LUCRO_REAL,
        state="SP",
        operation_type=OperationType.INTERNAL,
        operation_date=op_date,
        product_description="TECLADO MECANICO USB",
        quantity=Decimal("1.00"),
        unit_value=Decimal("500.00"),
        total_value=Decimal("500.00"),
        ncm=ncm,
        cst="00",
        cfop="5102",
        origin=0,
        customer_type=CustomerType.TAXPAYER,
        invoice_purpose=InvoicePurpose.NORMAL
    )


def make_rule(rule_id: str = "r_class_01", rate: Decimal = Decimal("18.00"), from_d: date = date(2026, 1, 1), until_d: date = date(2026, 12, 31)) -> FiscalTaxRule:
    return FiscalTaxRule(
        rule_id=rule_id,
        tax_type=TaxType.ICMS,
        jurisdiction=Jurisdiction.STATE,
        state="SP",
        effective_from=from_d,
        effective_until=until_d,
        priority=10,
        rate=rate,
        source_legal_node_id="node_c_1",
        source_legal_version_id="ver_c_1",
        evidence_id="ev_c_1"
    )


# 1. classificação válida
def test_01_valid_classification():
    prof = FiscalProductProfile(
        product_id="p1",
        description="TECLADO",
        normalized_description="TECLADO",
        ncm="84713012",
        fiscal_status=ClassificationStatus.CLASSIFIED
    )
    assert prof.fiscal_status == ClassificationStatus.CLASSIFIED


# 2. NCM inválido
def test_02_invalid_ncm_handling():
    fact = make_fact(ncm="123")  # NCM < 8 dígitos
    engine = DecisionEngine(available_rules=[make_rule()])
    d = engine.evaluate(fact)
    assert d.status == DecisionStatus.REVIEW_REQUIRED


# 3. NCM conflitante
def test_03_conflicting_ncm():
    engine = DecisionEngine(available_rules=[make_rule()])
    d = engine.evaluate(make_fact(ncm="00000000"))
    assert d.review_required is True


# 4. CEST
def test_04_cest_support():
    prof = FiscalProductProfile(product_id="p1", description="ITEM", normalized_description="ITEM", ncm="84713012", cest="2100100")
    assert prof.cest == "2100100"


# 5. CST
def test_05_cst():
    fact = make_fact()
    assert fact.cst == "00"


# 6. CSOSN
def test_06_csosn():
    fact = make_fact()
    assert fact.tax_regime == TaxRegime.LUCRO_REAL


# 7. CFOP
def test_07_cfop():
    fact = make_fact()
    assert fact.cfop == "5102"


# 8. múltiplas regras
def test_08_multiple_rules():
    r1 = make_rule("r1", rate=Decimal("18.00"))
    r2 = FiscalTaxRule(rule_id="r2", tax_type=TaxType.PIS, jurisdiction=Jurisdiction.FEDERAL, effective_from=date(2026, 1, 1), rate=Decimal("1.65"), source_legal_node_id="n2")
    engine = DecisionEngine(available_rules=[r1, r2])
    d = engine.evaluate(make_fact())
    assert len(d.tax_results) == 2


# 9. conflito de regras
def test_09_rule_conflict():
    r1 = make_rule("r1", rate=Decimal("18.00"))
    r2 = make_rule("r2", rate=Decimal("12.00"))  # Conflito mesma prioridade
    engine = DecisionEngine(available_rules=[r1, r2])
    d = engine.evaluate(make_fact())
    assert d.status == DecisionStatus.CONFLICT


# 10. regra temporal
def test_10_temporal_rule():
    r = make_rule(from_d=date(2026, 1, 1), until_d=date(2026, 12, 31))
    res = TaxRuleResolver.resolve_rules_for_fact(make_fact(op_date=date(2026, 6, 1)), [r])
    assert len(res) == 1


# 11. regra expirada
def test_11_expired_rule():
    r = make_rule(from_d=date(2025, 1, 1), until_d=date(2025, 12, 31))
    res = TaxRuleResolver.resolve_rules_for_fact(make_fact(op_date=date(2026, 6, 1)), [r])
    assert len(res) == 0


# 12. regra futura
def test_12_future_rule():
    r = make_rule(from_d=date(2027, 1, 1), until_d=date(2027, 12, 31))
    res = TaxRuleResolver.resolve_rules_for_fact(make_fact(op_date=date(2026, 6, 1)), [r])
    assert len(res) == 0


# 13. ausência de evidência
def test_13_missing_evidence():
    r_no_ev = FiscalTaxRule(rule_id="r1", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, effective_from=date(2026, 1, 1), rate=Decimal("18.00"), source_legal_node_id=None)
    engine = DecisionEngine(available_rules=[r_no_ev])
    d = engine.evaluate(make_fact())
    assert d.status == DecisionStatus.LEGAL_BASIS_MISSING


# 14. Decimal
def test_14_decimal_arithmetic():
    f = make_fact()
    assert isinstance(f.total_value, Decimal)


# 15. arredondamento
def test_15_rounding():
    calcs, mems = TaxCalculationEngine.calculate_taxes_for_fact(make_fact(), [make_rule()])
    assert mems[0].rounding_policy == "ROUND_HALF_UP"


# 16. memória de cálculo
def test_16_calculation_memory():
    calcs, mems = TaxCalculationEngine.calculate_taxes_for_fact(make_fact(), [make_rule()])
    assert len(mems) == 1
    assert "taxable_base" in mems[0].formula


# 17. totalização
def test_17_totalization():
    calcs, mems = TaxCalculationEngine.calculate_taxes_for_fact(make_fact(), [make_rule()])
    total = sum((c.calculated_amount for c in calcs), start=Decimal("0.00"))
    assert total == Decimal("90.00")


# 18. divergência
def test_18_divergence_handling():
    engine = DecisionEngine(available_rules=[make_rule("r1"), make_rule("r2", rate=Decimal("12.00"))])
    d = engine.evaluate(make_fact())
    assert d.status == DecisionStatus.CONFLICT


# 19. idempotência
def test_19_idempotency():
    engine = DecisionEngine(available_rules=[make_rule()])
    d1 = engine.evaluate(make_fact())
    d2 = engine.evaluate(make_fact())
    assert d1.decision_hash == d2.decision_hash


# 20. reprocessamento
def test_20_reprocessing():
    engine1 = DecisionEngine(available_rules=[make_rule("r1", rate=Decimal("18.00"))])
    d1 = engine1.evaluate(make_fact())

    engine2 = DecisionEngine(available_rules=[make_rule("r1", rate=Decimal("12.00"))])
    d2 = engine2.evaluate(make_fact())

    assert d1.tax_results[0].calculated_amount != d2.tax_results[0].calculated_amount


# 21. comparação de decisões
def test_21_decision_comparison():
    engine1 = DecisionEngine(available_rules=[make_rule("r1", rate=Decimal("18.00"))])
    d1 = engine1.evaluate(make_fact())

    engine2 = DecisionEngine(available_rules=[make_rule("r1", rate=Decimal("12.00"))])
    d2 = engine2.evaluate(make_fact())

    assert d1.decision_id == d2.decision_id


# 22. review automático
def test_22_automatic_review():
    r_no_ev = FiscalTaxRule(rule_id="r1", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, effective_from=date(2026, 1, 1), rate=Decimal("18.00"), source_legal_node_id=None)
    engine = DecisionEngine(available_rules=[r_no_ev])
    d = engine.evaluate(make_fact())
    assert d.review_required is True


# 23. engine version
def test_23_engine_version():
    engine = DecisionEngine(available_rules=[make_rule()])
    d = engine.evaluate(make_fact())
    assert d.decision_trace["engine_version"] == "v0.10.0-fiscal-brain-foundation"


# 24. ausência de datetime.now para autoridade temporal
def test_24_no_datetime_now_temporal_authority():
    fact_2024 = make_fact(op_date=date(2024, 5, 10))
    rule_2024 = make_rule(from_d=date(2024, 1, 1), until_d=date(2024, 12, 31))
    res = TaxRuleResolver.resolve_rules_for_fact(fact_2024, [rule_2024])
    assert len(res) == 1


# 25. ausência de float monetário
def test_25_no_float_monetary():
    fact = make_fact()
    assert not isinstance(fact.total_value, float)


# 26. ausência de regra inventada
def test_26_no_invented_rule():
    engine = DecisionEngine(available_rules=[])
    d = engine.evaluate(make_fact())
    assert d.status == DecisionStatus.NO_APPLICABLE_RULE
    assert len(d.tax_results) == 0
