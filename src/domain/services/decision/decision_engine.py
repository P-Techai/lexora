import hashlib
import json
from datetime import date
from typing import Any, Dict, List, Optional

from src.domain.decision.decision import Decision
from src.domain.decision.decision_trace import DecisionTrace
from src.domain.enums import ClassificationStatus, DecisionStatus, TaxType
from src.domain.fiscal.fiscal_classification import FiscalClassification
from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.fiscal.tax_calculation import TaxCalculation
from src.domain.services.fiscal.fiscal_classifier import FiscalClassifier
from src.domain.services.fiscal.tax_calculator import TaxCalculator
from src.domain.services.fiscal.tax_rule_evaluator import TaxRuleEvaluator


class DecisionEngine:
    """
    Cérebro de Decisão (Decision Engine) da LÉXORA.
    Orquestra Two-Brain Flow (Legal Brain + Fiscal Brain) de forma 100% determinística.
    NUNCA utiliza LLM para cálculos ou decisões tributárias.
    """

    def __init__(self, available_rules: Optional[List[FiscalTaxRule]] = None):
        self.available_rules = available_rules or []

    def evaluate(self, fact: FiscalFact, override_rules: Optional[List[FiscalTaxRule]] = None) -> Decision:
        rules = override_rules if override_rules is not None else self.available_rules

        trace_steps: List[Dict[str, Any]] = []
        warnings: List[str] = []
        conflicts: List[Dict[str, Any]] = []

        # 1. Step INPUT
        trace_steps.append({
            "stage": "INPUT",
            "fact_id": fact.fact_id,
            "operation_date": fact.operation_date.isoformat(),
            "total_value": str(fact.total_value)
        })

        # 2. Step NORMALIZATION & CLASSIFICATION
        classification: FiscalClassification = FiscalClassifier.classify_fact(fact)
        trace_steps.append({
            "stage": "CLASSIFICATION",
            "classification_status": classification.status.value,
            "ncm": classification.ncm,
            "cst": classification.cst,
            "cfop": classification.cfop,
            "reasons": classification.reasons
        })

        review_required = (classification.status == ClassificationStatus.REVIEW_REQUIRED)

        # 3. Step RULE_SELECTION & TEMPORAL_VALIDATION
        matching_rules = TaxRuleEvaluator.find_matching_rules(fact, rules)
        trace_steps.append({
            "stage": "RULE_SELECTION",
            "matching_rule_count": len(matching_rules),
            "rule_ids": [r.rule_id for r in matching_rules]
        })

        if not matching_rules:
            status = DecisionStatus.NO_APPLICABLE_RULE
            warnings.append("Nenhuma regra fiscal aplicável encontrada para a data de referência solicitada.")
            review_required = True
        else:
            # Checagem de conflitos entre regras com mesma prioridade e tributo
            conflicting = self._detect_conflicts(matching_rules)
            if conflicting:
                status = DecisionStatus.CONFLICT
                conflicts.extend(conflicting)
                warnings.append("Detectado conflito normativo entre regras fiscais aplicáveis.")
                review_required = True
            elif review_required:
                status = DecisionStatus.REVIEW_REQUIRED
            else:
                status = DecisionStatus.APPROVED

        # 4. Step CALCULATION & LEGAL_VALIDATION
        tax_results: List[TaxCalculation] = []
        applied_rules: List[FiscalTaxRule] = []
        legal_basis: List[Dict[str, Any]] = []

        if status in (DecisionStatus.APPROVED, DecisionStatus.REVIEW_REQUIRED):
            # Agrupa melhor regra por tax_type
            rules_by_type: Dict[TaxType, FiscalTaxRule] = {}
            for r in matching_rules:
                if r.tax_type not in rules_by_type:
                    rules_by_type[r.tax_type] = r

            for tax_type, rule in rules_by_type.items():
                calc = TaxCalculator.calculate_tax(fact, rule)
                tax_results.append(calc)
                applied_rules.append(rule)

                # Verifica fundamentação legal
                if not rule.source_legal_node_id or not rule.source_legal_version_id or not rule.evidence_id:
                    warnings.append(f"Regra {rule.rule_id} para {tax_type.value} sem fundamentação legal/evidência cadastrada.")
                    if status == DecisionStatus.APPROVED:
                        status = DecisionStatus.REVIEW_REQUIRED
                        review_required = True
                else:
                    legal_basis.append({
                        "tax_type": tax_type.value,
                        "rule_id": rule.rule_id,
                        "source_legal_node_id": rule.source_legal_node_id,
                        "source_legal_version_id": rule.source_legal_version_id,
                        "evidence_id": rule.evidence_id
                    })

        trace_steps.append({
            "stage": "CALCULATION",
            "calculated_taxes_count": len(tax_results),
            "status": status.value
        })

        # 5. Hashes SHA-256 determinísticos
        input_hash = hashlib.sha256(fact.model_dump_json().encode("utf-8")).hexdigest()
        rule_snapshot_hash = hashlib.sha256(
            json.dumps([r.model_dump(mode="json") for r in applied_rules], sort_keys=True).encode("utf-8")
        ).hexdigest()
        calc_hash = hashlib.sha256(
            json.dumps([c.model_dump(mode="json") for c in tax_results], sort_keys=True).encode("utf-8")
        ).hexdigest()

        decision_raw_data = f"{input_hash}|{rule_snapshot_hash}|{calc_hash}|{status.value}|{fact.operation_date.isoformat()}"
        decision_id = f"dec_{hashlib.sha256(decision_raw_data.encode('utf-8')).hexdigest()[:16]}"
        decision_hash = hashlib.sha256(decision_raw_data.encode("utf-8")).hexdigest()

        trace = DecisionTrace(
            trace_id=f"trc_{decision_id[4:]}",
            decision_id=decision_id,
            steps=trace_steps,
            input_hash=input_hash,
            rule_snapshot_hash=rule_snapshot_hash,
            calculation_hash=calc_hash
        )

        return Decision(
            decision_id=decision_id,
            status=status,
            classification=classification,
            tax_results=tax_results,
            applied_rules=applied_rules,
            legal_basis=legal_basis,
            warnings=warnings,
            conflicts=conflicts,
            review_required=review_required,
            decision_trace=trace.model_dump(mode="json"),
            reference_date=fact.operation_date,
            decision_hash=decision_hash
        )

    def _detect_conflicts(self, rules: List[FiscalTaxRule]) -> List[Dict[str, Any]]:
        conflicts: List[Dict[str, Any]] = []
        by_type_priority: Dict[Tuple[TaxType, int], List[FiscalTaxRule]] = {}

        for r in rules:
            key = (r.tax_type, r.priority)
            by_type_priority.setdefault(key, []).append(r)

        for (tax_type, priority), rule_group in by_type_priority.items():
            if len(rule_group) > 1:
                # Verifica se as alíquotas ou fórmulas diferem
                rates = {r.rate for r in rule_group}
                if len(rates) > 1:
                    conflicts.append({
                        "tax_type": tax_type.value,
                        "priority": priority,
                        "conflicting_rule_ids": [r.rule_id for r in rule_group],
                        "rates": [str(r.rate) for r in rule_group],
                        "reason": f"Conflito entre {len(rule_group)} regras de {tax_type.value} com mesma prioridade {priority} e alíquotas distintas."
                    })

        return conflicts
