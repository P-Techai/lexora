from typing import Any, Dict, List

from src.domain.decision.decision import Decision
from src.domain.enums import DecisionStatus


class FiscalCopilotService:
    """
    Serviço assistente de Co-Pilot Fiscal da LÉXORA.
    Explicador determinístico e gerador de síntese explicativa.
    LLM = EXPLANATION ONLY. O Co-Pilot NUNCA altera o resultado do DecisionEngine.
    """

    @staticmethod
    def explain_decision(decision: Decision, context_pack: str = "") -> Dict[str, Any]:
        """
        Gera uma explicação estruturada e auditável sobre a decisão fiscal.
        """
        applied_summary: List[Dict[str, Any]] = []
        for rule in decision.applied_rules:
            applied_summary.append({
                "rule_id": rule.rule_id,
                "tax_type": rule.tax_type.value,
                "rate": str(rule.rate),
                "base_reduction": str(rule.base_reduction),
                "jurisdiction": rule.jurisdiction.value,
                "effective_period": f"{rule.effective_from} a {rule.effective_until or 'indefinido'}",
                "source_legal_node_id": rule.source_legal_node_id
            })

        tax_summaries: List[Dict[str, Any]] = []
        for calc in decision.tax_results:
            tax_summaries.append({
                "tax_type": calc.tax_type.value,
                "taxable_base": str(calc.taxable_base),
                "rate": str(calc.rate),
                "calculated_amount": str(calc.calculated_amount),
                "formula": calc.formula
            })

        status_explanation = ""
        if decision.status == DecisionStatus.APPROVED:
            status_explanation = "Decisão aprovada com fundamentação legal e cálculos determinísticos validados."
        elif decision.status in (DecisionStatus.REVIEW_REQUIRED, DecisionStatus.REQUIRES_HUMAN_REVIEW):
            status_explanation = "Revisão humana necessária devido a dados cadastrais incompletos ou ausência de fundamentação normativa direta."
        elif decision.status in (DecisionStatus.CONFLICT, DecisionStatus.FISCAL_RULE_CONFLICT):
            status_explanation = "Conflito normativo detectado entre regras ativas com mesma prioridade."
        elif decision.status in (DecisionStatus.NO_APPLICABLE_RULE, DecisionStatus.FISCAL_RULE_NOT_FOUND, DecisionStatus.RULE_NOT_FOUND):
            status_explanation = "Nenhuma regra tributária ativa encontrada para a data de referência informada."

        explanation_text = (
            f"Decisão {decision.decision_id} (Status: {decision.status.value}). "
            f"{status_explanation} "
            f"Tributos calculados: {len(decision.tax_results)}. "
            f"Fundamentações jurídicas vinculadas: {len(decision.legal_basis)}."
        )

        return {
            "decision_id": decision.decision_id,
            "status": decision.status.value,
            "summary_text": explanation_text,
            "applied_rules_breakdown": applied_summary,
            "tax_calculations_breakdown": tax_summaries,
            "legal_basis_links": decision.legal_basis,
            "warnings": decision.warnings,
            "conflicts": decision.conflicts,
            "review_required": decision.review_required,
            "decision_hash": decision.decision_hash
        }
