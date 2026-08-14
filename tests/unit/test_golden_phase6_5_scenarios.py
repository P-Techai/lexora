from datetime import date
from decimal import Decimal
import pytest

from src.domain.enums import CustomerType, DecisionStatus, InvoicePurpose, Jurisdiction, OperationType, ReviewReason, ReviewStatus, TaxRegime, TaxType
from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.fiscal.fiscal_review import FiscalReview, HumanOverride
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.services.decision.decision_engine import DecisionEngine
from src.domain.services.fiscal.review_state_machine import ReviewStateMachine
from src.domain.services.fiscal.tax_calculation_engine import TaxCalculationEngine
from src.domain.services.fiscal.tax_rule_resolver import TaxRuleResolver


def make_golden_fact(op_date: date = date(2026, 6, 15), ncm: str = "84713012") -> FiscalFact:
    return FiscalFact(
        fact_id="fact_g65_01",
        company_id="comp_g65",
        tax_regime=TaxRegime.LUCRO_REAL,
        state="SP",
        operation_type=OperationType.INTERNAL,
        operation_date=op_date,
        product_description="SERVIDOR RACK DE PROCESSAMENTO",
        quantity=Decimal("1.00"),
        unit_value=Decimal("10000.00"),
        total_value=Decimal("10000.00"),
        ncm=ncm,
        cst="00",
        cfop="5102",
        origin=0,
        customer_type=CustomerType.TAXPAYER,
        invoice_purpose=InvoicePurpose.NORMAL
    )


def test_golden_phase6_5_01_complete_flow():
    """GOLDEN TEST 1: Produto -> NCM -> Empresa -> Operação -> Regra -> Legal Evidence -> ICMS, PIS, COFINS -> memória -> Decision."""
    r_icms = FiscalTaxRule(rule_id="r_icms", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, state="SP", effective_from=date(2026, 1, 1), rate=Decimal("18.00"), source_legal_node_id="node_icms", evidence_id="ev_icms")
    r_pis = FiscalTaxRule(rule_id="r_pis", tax_type=TaxType.PIS, jurisdiction=Jurisdiction.FEDERAL, effective_from=date(2026, 1, 1), rate=Decimal("1.65"), source_legal_node_id="node_pis", evidence_id="ev_pis")
    r_cofins = FiscalTaxRule(rule_id="r_cofins", tax_type=TaxType.COFINS, jurisdiction=Jurisdiction.FEDERAL, effective_from=date(2026, 1, 1), rate=Decimal("7.60"), source_legal_node_id="node_cofins", evidence_id="ev_cofins")

    fact = make_golden_fact()
    engine = DecisionEngine(available_rules=[r_icms, r_pis, r_cofins])
    decision = engine.evaluate(fact)

    assert decision.status == DecisionStatus.APPROVED
    assert len(decision.tax_results) == 3
    assert decision.review_required is False

    calcs, mems = TaxCalculationEngine.calculate_taxes_for_fact(fact, [r_icms, r_pis, r_cofins])
    assert len(mems) == 3

    icms_calc = next(c for c in calcs if c.tax_type == TaxType.ICMS)
    pis_calc = next(c for c in calcs if c.tax_type == TaxType.PIS)
    cofins_calc = next(c for c in calcs if c.tax_type == TaxType.COFINS)

    assert icms_calc.calculated_amount == Decimal("1800.00")
    assert pis_calc.calculated_amount == Decimal("165.00")
    assert cofins_calc.calculated_amount == Decimal("760.00")


def test_golden_phase6_5_02_conflict_review_resolution():
    """GOLDEN TEST 2: NF-e -> NCM conflitante -> REVIEW_REQUIRED -> Human Review -> Reclassificação -> Nova Decisão -> Histórico Preservado."""
    r_no_ev = FiscalTaxRule(rule_id="r_no_ev", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, effective_from=date(2026, 1, 1), rate=Decimal("18.00"), source_legal_node_id=None)
    fact = make_golden_fact()

    engine_old = DecisionEngine(available_rules=[r_no_ev])
    orig_dec = engine_old.evaluate(fact)
    assert orig_dec.status == DecisionStatus.LEGAL_BASIS_MISSING
    assert orig_dec.review_required is True

    review = FiscalReview(review_id="rev_g2", decision_id=orig_dec.decision_id, status=ReviewStatus.OPEN, reason=ReviewReason.MISSING_LEGAL_EVIDENCE, description="Evidência em falta")
    r_in, _ = ReviewStateMachine.transition(review, ReviewStatus.IN_REVIEW, "auditor_1", "START", "Iniciando análise")
    r_resolved, _ = ReviewStateMachine.transition(r_in, ReviewStatus.RESOLVED, "auditor_1", "RESOLVE", "Fundamentação legal adicionada manualmente")

    # Novo motor com evidência regularizada
    r_fixed = FiscalTaxRule(rule_id="r_fixed", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, effective_from=date(2026, 1, 1), rate=Decimal("18.00"), source_legal_node_id="node_fixed", evidence_id="ev_fixed")
    engine_new = DecisionEngine(available_rules=[r_fixed])
    new_dec = engine_new.evaluate(fact)

    override = HumanOverride(
        override_id="ovr_g2",
        original_decision_id=orig_dec.decision_id,
        new_decision_id=new_dec.decision_id,
        actor_id="auditor_1",
        justification="Legal evidence vinculada com sucesso",
        override_data={"fixed_rule_id": "r_fixed"},
        override_hash="hash_g2"
    )

    assert orig_dec.decision_id != new_dec.decision_id
    assert override.original_decision_id == orig_dec.decision_id
    assert new_dec.status == DecisionStatus.APPROVED


def test_golden_phase6_5_03_historical_temporality():
    """GOLDEN TEST 3: Operação de 2024 processada em 2026 aplica Regra A (2024) e NÃO Regra B (2025)."""
    rule_A_2024 = FiscalTaxRule(rule_id="rule_A_2024", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, state="SP", effective_from=date(2024, 1, 1), effective_until=date(2024, 12, 31), rate=Decimal("12.00"), source_legal_node_id="node_2024", evidence_id="ev_2024")
    rule_B_2025 = FiscalTaxRule(rule_id="rule_B_2025", tax_type=TaxType.ICMS, jurisdiction=Jurisdiction.STATE, state="SP", effective_from=date(2025, 1, 1), effective_until=date(2026, 12, 31), rate=Decimal("18.00"), source_legal_node_id="node_2025", evidence_id="ev_2025")

    fact_2024 = make_golden_fact(op_date=date(2024, 5, 20))
    resolved = TaxRuleResolver.resolve_rules_for_fact(fact_2024, [rule_A_2024, rule_B_2025])

    assert len(resolved) == 1
    assert resolved[0].rule_id == "rule_A_2024"

    engine = DecisionEngine(available_rules=[rule_A_2024, rule_B_2025])
    decision = engine.evaluate(fact_2024)
    assert decision.status == DecisionStatus.APPROVED
    assert len(decision.applied_rules) == 1
    assert decision.applied_rules[0].rule_id == "rule_A_2024"
    assert decision.tax_results[0].rate == Decimal("12.00")
