from datetime import date
from decimal import Decimal
import pytest

from src.domain.enums import CustomerType, DecisionStatus, InvoicePurpose, Jurisdiction, OperationType, ReviewReason, ReviewStatus, TaxRegime, TaxType
from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.fiscal.fiscal_review import FiscalReview, HumanOverride
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.services.decision.decision_engine import DecisionEngine
from src.domain.services.fiscal.fiscal_diff_engine import FiscalDiffEngine
from src.domain.services.fiscal.review_state_machine import ReviewStateMachine


def make_golden_fact() -> FiscalFact:
    return FiscalFact(
        fact_id="fact_gr_01",
        company_id="comp_gr",
        tax_regime=TaxRegime.LUCRO_REAL,
        state="SP",
        operation_type=OperationType.INTERNAL,
        operation_date=date(2026, 6, 1),
        product_description="NOTEBOOK TESTE GOLDEN",
        quantity=Decimal("1.00"),
        unit_value=Decimal("1000.00"),
        total_value=Decimal("1000.00"),
        ncm="84713012",
        cst="00",
        cfop="5102",
        origin=0,
        customer_type=CustomerType.TAXPAYER,
        invoice_purpose=InvoicePurpose.NORMAL
    )


def make_golden_rule(rate: Decimal = Decimal("18.00")) -> FiscalTaxRule:
    return FiscalTaxRule(
        rule_id="rule_gr_01",
        tax_type=TaxType.ICMS,
        jurisdiction=Jurisdiction.STATE,
        state="SP",
        effective_from=date(2026, 1, 1),
        effective_until=date(2026, 12, 31),
        priority=10,
        rate=rate,
        source_legal_node_id="node_gr_1",
        source_legal_version_id="ver_gr_1",
        evidence_id="ev_gr_1"
    )


def test_golden_review_001_approved_flow():
    """GOLDEN-REVIEW-001: Decisão APPROVED -> Consulta -> Revisão -> Aprovação -> Audit Trail."""
    engine = DecisionEngine(available_rules=[make_golden_rule()])
    decision = engine.evaluate(make_golden_fact())
    assert decision.status == DecisionStatus.APPROVED

    review = FiscalReview(
        review_id="rev_gr_1",
        decision_id=decision.decision_id,
        status=ReviewStatus.OPEN,
        reason=ReviewReason.OTHER,
        description="Revisão preventiva"
    )
    r_in_review, evt_start = ReviewStateMachine.transition(review, ReviewStatus.IN_REVIEW, "auditor_1", "START", "Iniciando")
    r_approved, evt_app = ReviewStateMachine.transition(r_in_review, ReviewStatus.APPROVED, "auditor_1", "APPROVE", "Evidência confirmada")

    assert r_approved.status == ReviewStatus.APPROVED
    assert len(evt_app.event_hash) == 64


def test_golden_review_002_correction_override():
    """GOLDEN-REVIEW-002: Decisão REVIEW_REQUIRED -> Revisão -> Correção/Override -> Novo Resultado (Decisão Original Preservada)."""
    # Regra sem base legal gera REVIEW_REQUIRED
    rule_no_basis = FiscalTaxRule(
        rule_id="r_nobasis",
        tax_type=TaxType.ICMS,
        jurisdiction=Jurisdiction.STATE,
        effective_from=date(2026, 1, 1),
        rate=Decimal("18.00"),
        source_legal_node_id=None  # Sem nó legal
    )
    engine = DecisionEngine(available_rules=[rule_no_basis])
    orig_dec = engine.evaluate(make_golden_fact())
    assert orig_dec.status == DecisionStatus.REVIEW_REQUIRED

    # Novo motor com regra corrigida
    engine_fixed = DecisionEngine(available_rules=[make_golden_rule()])
    new_dec = engine_fixed.evaluate(make_golden_fact())
    assert new_dec.status == DecisionStatus.APPROVED

    override = HumanOverride(
        override_id="ovr_gr_2",
        original_decision_id=orig_dec.decision_id,
        new_decision_id=new_dec.decision_id,
        actor_id="auditor_legal",
        justification="Fundamentação jurídica informada manualmente pelo auditor",
        override_data={"new_rule_id": "rule_gr_01"},
        override_hash="hash_ovr_gr_2"
    )

    # A decisão original permanece intacta
    assert orig_dec.decision_id != new_dec.decision_id
    assert override.original_decision_id == orig_dec.decision_id


def test_golden_review_003_conflict_escalation():
    """GOLDEN-REVIEW-003: CONFLICT -> Revisão -> ESCALATED -> Audit Trail."""
    r1 = FiscalTaxRule(rule_id="r1", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, effective_from=date(2026, 1, 1), priority=10, rate=Decimal("18.00"))
    r2 = FiscalTaxRule(rule_id="r2", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, effective_from=date(2026, 1, 1), priority=10, rate=Decimal("12.00"))
    engine = DecisionEngine(available_rules=[r1, r2])
    conflict_dec = engine.evaluate(make_golden_fact())
    assert conflict_dec.status == DecisionStatus.CONFLICT

    review = FiscalReview(
        review_id="rev_gr_3",
        decision_id=conflict_dec.decision_id,
        status=ReviewStatus.OPEN,
        reason=ReviewReason.RULE_CONFLICT,
        description="Conflito normativo de ICMS"
    )
    r_in, _ = ReviewStateMachine.transition(review, ReviewStatus.IN_REVIEW, "auditor_jr", "START", "Iniciando")
    r_esc, evt_esc = ReviewStateMachine.transition(r_in, ReviewStatus.ESCALATED, "auditor_jr", "ESCALATE", "Escalado para comitê jurídico")

    assert r_esc.status == ReviewStatus.ESCALATED
    assert len(evt_esc.event_hash) == 64


def test_golden_review_004_reprocess_diff():
    """GOLDEN-REVIEW-004: REPROCESS -> Comparação OLD Result vs NEW Result."""
    engine_old = DecisionEngine(available_rules=[make_golden_rule(rate=Decimal("18.00"))])
    old_dec = engine_old.evaluate(make_golden_fact())

    engine_new = DecisionEngine(available_rules=[make_golden_rule(rate=Decimal("12.00"))])
    new_dec = engine_new.evaluate(make_golden_fact())

    diff = FiscalDiffEngine.compare_decisions(old_dec, new_dec)
    assert diff["has_differences"] is True
    assert "ICMS" in diff["tax_amount_diff"]
    assert diff["tax_amount_diff"]["ICMS"]["old_amount"] == "180.00"
    assert diff["tax_amount_diff"]["ICMS"]["new_amount"] == "120.00"
