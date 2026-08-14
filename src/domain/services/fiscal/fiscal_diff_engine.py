from typing import Any, Dict
from src.domain.decision.decision import Decision


class FiscalDiffEngine:
    """
    Motor de comparação e Fiscal Diff entre duas decisões (ex: Decisão Histórica vs Decisão Reprocessada).
    """

    @staticmethod
    def compare_decisions(old_decision: Decision, new_decision: Decision) -> Dict[str, Any]:
        old_cls = old_decision.classification
        new_cls = new_decision.classification

        ncm_changed = (old_cls.ncm != new_cls.ncm)
        cst_changed = (old_cls.cst != new_cls.cst)
        cfop_changed = (old_cls.cfop != new_cls.cfop)
        status_changed = (old_decision.status != new_decision.status)

        old_rules = {r.rule_id for r in old_decision.applied_rules}
        new_rules = {r.rule_id for r in new_decision.applied_rules}
        applied_rules_changed = (old_rules != new_rules)

        old_taxes = {c.tax_type.value: str(c.calculated_amount) for c in old_decision.tax_results}
        new_taxes = {c.tax_type.value: str(c.calculated_amount) for c in new_decision.tax_results}

        tax_diff: Dict[str, Dict[str, str]] = {}
        all_tax_keys = set(old_taxes.keys()).union(new_taxes.keys())
        for k in all_tax_keys:
            v_old = old_taxes.get(k, "0.00")
            v_new = new_taxes.get(k, "0.00")
            if v_old != v_new:
                tax_diff[k] = {"old_amount": v_old, "new_amount": v_new}

        old_legal = {b.get("source_legal_node_id") for b in old_decision.legal_basis}
        new_legal = {b.get("source_legal_node_id") for b in new_decision.legal_basis}
        legal_basis_changed = (old_legal != new_legal)

        has_differences = (
            ncm_changed or cst_changed or cfop_changed or status_changed
            or applied_rules_changed or len(tax_diff) > 0 or legal_basis_changed
        )

        return {
            "old_decision_id": old_decision.decision_id,
            "new_decision_id": new_decision.decision_id,
            "has_differences": has_differences,
            "status_changed": status_changed,
            "old_status": old_decision.status.value,
            "new_status": new_decision.status.value,
            "ncm_changed": ncm_changed,
            "old_ncm": old_cls.ncm,
            "new_ncm": new_cls.ncm,
            "cst_changed": cst_changed,
            "cfop_changed": cfop_changed,
            "applied_rules_changed": applied_rules_changed,
            "tax_amount_diff": tax_diff,
            "legal_basis_changed": legal_basis_changed
        }
