from datetime import date
from decimal import Decimal
import pytest

from src.domain.enums import CustomerType, DecisionStatus, InvoicePurpose, Jurisdiction, OperationType, TaxRegime, TaxType
from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.services.decision.decision_engine import DecisionEngine


# Fixtures sintéticas claramente marcadas como TEST_FIXTURE / SYNTHETIC_RULE conforme Prompt 12 §30
SYNTHETIC_RULE_ICMS_SP = FiscalTaxRule(
    rule_id="SYNTHETIC_RULE_GOLDEN_01",
    tax_type=TaxType.ICMS,
    jurisdiction=Jurisdiction.STATE,
    state="SP",
    effective_from=date(2026, 1, 1),
    effective_until=date(2026, 12, 31),
    priority=10,
    rate=Decimal("18.00"),
    source_legal_node_id="TEST_FIXTURE_NODE_01",
    source_legal_version_id="TEST_FIXTURE_VER_01",
    evidence_id="TEST_FIXTURE_EV_01"
)

SYNTHETIC_RULE_PIS_FED = FiscalTaxRule(
    rule_id="SYNTHETIC_RULE_GOLDEN_02",
    tax_type=TaxType.PIS,
    jurisdiction=Jurisdiction.FEDERAL,
    effective_from=date(2026, 1, 1),
    effective_until=date(2026, 12, 31),
    priority=10,
    rate=Decimal("1.65"),
    source_legal_node_id="TEST_FIXTURE_NODE_02",
    source_legal_version_id="TEST_FIXTURE_VER_02",
    evidence_id="TEST_FIXTURE_EV_02"
)

SYNTHETIC_RULE_CONFLICT_SP = FiscalTaxRule(
    rule_id="SYNTHETIC_RULE_GOLDEN_03_CONFLICT",
    tax_type=TaxType.ICMS,
    jurisdiction=Jurisdiction.STATE,
    state="SP",
    effective_from=date(2026, 1, 1),
    effective_until=date(2026, 12, 31),
    priority=10,  # Mesma prioridade 10
    rate=Decimal("12.00"),  # Alíquota conflitante (12% vs 18%)
    source_legal_node_id="TEST_FIXTURE_NODE_03",
    source_legal_version_id="TEST_FIXTURE_VER_03",
    evidence_id="TEST_FIXTURE_EV_03"
)


def make_golden_fact(
    op_date: date = date(2026, 6, 15),
    total_val: Decimal = Decimal("1000.00"),
    state: str = "SP"
) -> FiscalFact:
    return FiscalFact(
        fact_id="golden_fact_01",
        company_id="comp_golden",
        tax_regime=TaxRegime.LUCRO_REAL,
        state=state,
        operation_type=OperationType.INTERNAL,
        operation_date=op_date,
        product_description="PRODUTO TESTE GOLDEN",
        quantity=Decimal("1.00"),
        unit_value=total_val,
        total_value=total_val,
        ncm="84713012",
        cst="00",
        cfop="5102",
        origin=0,
        customer_type=CustomerType.TAXPAYER,
        invoice_purpose=InvoicePurpose.NORMAL
    )


def test_golden_fiscal_01_simple_calculation():
    """GOLDEN-FISCAL-01: Cálculo simples de ICMS e PIS com regras sintéticas válidas."""
    fact = make_golden_fact()
    engine = DecisionEngine(available_rules=[SYNTHETIC_RULE_ICMS_SP, SYNTHETIC_RULE_PIS_FED])
    decision = engine.evaluate(fact)

    assert decision.status == DecisionStatus.APPROVED
    assert len(decision.tax_results) == 2
    assert decision.review_required is False

    icms_calc = next(c for c in decision.tax_results if c.tax_type == TaxType.ICMS)
    pis_calc = next(c for c in decision.tax_results if c.tax_type == TaxType.PIS)

    assert icms_calc.calculated_amount == Decimal("180.00")
    assert pis_calc.calculated_amount == Decimal("16.50")


def test_golden_fiscal_02_temporal_expiration():
    """GOLDEN-FISCAL-02: Mudança temporal com expiração de regra na data da operação."""
    # Operação em 2027 (fora do intervalo 2026 das regras sintéticas)
    fact = make_golden_fact(op_date=date(2027, 1, 15))
    engine = DecisionEngine(available_rules=[SYNTHETIC_RULE_ICMS_SP, SYNTHETIC_RULE_PIS_FED])
    decision = engine.evaluate(fact)

    assert decision.status == DecisionStatus.NO_APPLICABLE_RULE
    assert decision.review_required is True
    assert len(decision.tax_results) == 0


def test_golden_fiscal_03_explicit_conflict():
    """GOLDEN-FISCAL-03: Conflito normativo explícito entre regras de mesma prioridade."""
    fact = make_golden_fact()
    engine = DecisionEngine(available_rules=[SYNTHETIC_RULE_ICMS_SP, SYNTHETIC_RULE_CONFLICT_SP])
    decision = engine.evaluate(fact)

    assert decision.status == DecisionStatus.CONFLICT
    assert decision.review_required is True
    assert len(decision.conflicts) > 0
    assert "SYNTHETIC_RULE_GOLDEN_01" in decision.conflicts[0]["conflicting_rule_ids"]
