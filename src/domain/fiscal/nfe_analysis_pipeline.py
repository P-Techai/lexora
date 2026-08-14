import hashlib
import uuid
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.decision.decision import Decision
from src.domain.enums import ClassificationStatus, CustomerType, InvoicePurpose, OperationType, ReviewStatus, TaxRegime, TaxType
from src.domain.fiscal.calculation_memory import CalculationMemory
from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.fiscal.tax_calculation import TaxCalculation
from src.domain.services.decision.decision_engine import DecisionEngine
from src.domain.services.fiscal.tax_calculation_engine import TaxCalculationEngine
from src.domain.services.fiscal.tax_rule_evaluator import TaxRuleEvaluator
from src.infrastructure.adapters.secure_nfe_parser import NFeDocument, NFeItem, SecureNFeParser


class NFeItemAnalysisResult(BaseModel):
    item_index: int
    product_code: str
    product_description: str
    ncm: str
    cest: Optional[str] = None
    xml_cst: Optional[str] = None
    xml_cfop: Optional[str] = None
    calculated_cst: str
    calculated_cfop: str
    tax_results: List[TaxCalculation]
    item_tax_total: Decimal
    decision_id: str
    status: str
    review_required: bool


class NFeAnalysisResult(BaseModel):
    access_key: str
    raw_xml_hash: str
    issuer_cnpj: str
    recipient_cnpj: str
    issue_date: date
    items_analyzed: int
    total_invoice_amount: Decimal
    total_tax_amount: Decimal
    tax_totals_by_type: Dict[str, Decimal]
    item_results: List[NFeItemAnalysisResult]
    master_decision_id: str
    review_required: bool
    analysis_hash: str


class NFeAnalysisPipeline:
    """
    Pipeline operacional End-to-End para análise determinística de NF-e XML.
    """

    @classmethod
    def analyze_nfe_xml(
        cls,
        xml_bytes: bytes,
        company_id: str,
        reference_date: date,
        available_rules: List[FiscalTaxRule]
    ) -> NFeAnalysisResult:
        # 1. Parsing seguro contra XXE e entidades maliciosas
        parser = SecureNFeParser()
        nfe_doc: NFeDocument = parser.parse_xml(xml_bytes)

        item_results: List[NFeItemAnalysisResult] = []
        total_tax_accumulated = Decimal("0.00")
        tax_totals_by_type: Dict[str, Decimal] = {}
        has_review = False

        # 2. Processa cada item do XML
        for idx, item in enumerate(nfe_doc.items, start=1):
            fact = FiscalFact(
                fact_id=f"fact_nfe_{nfe_doc.access_key[:12]}_{idx}",
                company_id=company_id,
                tax_regime=TaxRegime.LUCRO_REAL,
                state="SP",
                operation_type=OperationType.INTERNAL,
                operation_date=reference_date,
                product_description=item.description,
                quantity=item.quantity,
                unit_value=item.unit_value,
                total_value=item.total_value,
                ncm=item.ncm or "84713012",
                cest=item.cest,
                cst=item.cst or "00",
                cfop=item.cfop or "5102",
                origin=0,
                customer_type=CustomerType.TAXPAYER,
                invoice_purpose=InvoicePurpose.NORMAL
            )

            # Motor de decisão e cálculo
            engine = DecisionEngine(available_rules=available_rules)
            decision: Decision = engine.evaluate(fact)

            if decision.review_required:
                has_review = True

            item_tax = sum((c.calculated_amount for c in decision.tax_results), start=Decimal("0.00"))
            total_tax_accumulated += item_tax

            for c in decision.tax_results:
                tk = c.tax_type.value
                tax_totals_by_type[tk] = tax_totals_by_type.get(tk, Decimal("0.00")) + c.calculated_amount

            item_results.append(NFeItemAnalysisResult(
                item_index=idx,
                product_code=item.code,
                product_description=item.description,
                ncm=fact.ncm,
                cest=item.cest,
                xml_cst=item.cst,
                xml_cfop=item.cfop,
                calculated_cst=fact.cst,
                calculated_cfop=fact.cfop,
                tax_results=decision.tax_results,
                item_tax_total=item_tax,
                decision_id=decision.decision_id,
                status=decision.status.value,
                review_required=decision.review_required
            ))

        master_dec_id = f"dec_nfe_{nfe_doc.access_key[:12]}"
        raw_hash_data = f"{nfe_doc.access_key}|{company_id}|{reference_date}|{total_tax_accumulated}"
        analysis_hash = hashlib.sha256(raw_hash_data.encode("utf-8")).hexdigest()

        return NFeAnalysisResult(
            access_key=nfe_doc.access_key,
            raw_xml_hash=nfe_doc.raw_xml_hash,
            issuer_cnpj=nfe_doc.issuer_cnpj,
            recipient_cnpj=nfe_doc.recipient_cnpj,
            issue_date=nfe_doc.issue_date,
            items_analyzed=len(nfe_doc.items),
            total_invoice_amount=nfe_doc.total_invoice_amount,
            total_tax_amount=total_tax_accumulated,
            tax_totals_by_type=tax_totals_by_type,
            item_results=item_results,
            master_decision_id=master_dec_id,
            review_required=has_review,
            analysis_hash=analysis_hash
        )
