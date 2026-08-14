import csv
import io
import json
from typing import Any, Dict, List

from src.domain.decision.decision import Decision


class AuditReportGenerator:
    """
    Gerador de relatórios estruturados de auditoria reconstruíveis a partir do banco de dados.
    """

    @staticmethod
    def generate_json_report(decision: Decision, reviews: Optional[List[Any]] = None) -> str:
        data = {
            "decision_id": decision.decision_id,
            "status": decision.status.value,
            "reference_date": str(decision.reference_date),
            "classification": decision.classification.model_dump(mode="json"),
            "applied_rules_count": len(decision.applied_rules),
            "tax_results": [c.model_dump(mode="json") for c in decision.tax_results],
            "legal_basis": decision.legal_basis,
            "warnings": decision.warnings,
            "conflicts": decision.conflicts,
            "review_required": decision.review_required,
            "decision_hash": decision.decision_hash,
            "decision_trace": decision.decision_trace,
            "reviews_history": reviews or []
        }
        return json.dumps(data, indent=2, ensure_ascii=False)

    @staticmethod
    def generate_csv_report(decision: Decision) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Decision ID", "Tax Type", "Taxable Base", "Rate (%)", "Calculated Amount", "Formula", "Legal Node ID", "Status"])

        for calc in decision.tax_results:
            legal_node = decision.legal_basis[0].get("source_legal_node_id", "N/A") if decision.legal_basis else "N/A"
            writer.writerow([
                decision.decision_id,
                calc.tax_type.value,
                str(calc.taxable_base),
                str(calc.rate),
                str(calc.calculated_amount),
                calc.formula,
                legal_node,
                decision.status.value
            ])

        return output.getvalue()
