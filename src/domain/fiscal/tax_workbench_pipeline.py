import hashlib
import uuid
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import ReviewStatus, TaxRegime
from src.domain.fiscal.company_fiscal_profile import CompanyFiscalProfile
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.fiscal.nfe_analysis_pipeline import NFeAnalysisPipeline, NFeAnalysisResult
from src.infrastructure.adapters.secure_nfe_parser import SecureNFeParser


class NFeLifecycleState(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATED = "VALIDATED"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    FAILED = "FAILED"


class ProductLifecycleState(str, Enum):
    UNCLASSIFIED = "UNCLASSIFIED"
    CLASSIFIED = "CLASSIFIED"
    HUMAN_REVIEW = "HUMAN_REVIEW"


class DecisionLifecycleState(str, Enum):
    PROPOSED = "PROPOSED"
    CONFIRMED = "CONFIRMED"
    HUMAN_REVIEW = "HUMAN_REVIEW"


class WorkbenchItemDetail(BaseModel):
    model_config = ConfigDict(frozen=True)

    item_index: int
    product_code: str
    product_description: str
    ncm: str
    cest: Optional[str] = None
    xml_cst: Optional[str] = None
    xml_cfop: Optional[str] = None
    calculated_cst: str
    calculated_cfop: str
    item_tax_total: Decimal
    product_state: ProductLifecycleState
    decision_state: DecisionLifecycleState
    decision_id: str


class WorkbenchNFeDocument(BaseModel):
    model_config = ConfigDict(frozen=True)

    nfe_id: str
    company_id: str
    access_key: str
    raw_xml_hash: str
    issue_date: date
    reference_date: date
    nfe_state: NFeLifecycleState
    total_invoice_amount: Decimal
    total_tax_amount: Decimal
    tax_totals_by_type: Dict[str, Decimal]
    items: List[WorkbenchItemDetail]
    master_decision_id: str
    review_required: bool
    document_hash: str


class OperationalTaxWorkbenchPipeline:
    """
    Pipeline funcional do Operational Tax Workbench do LÉXORA.
    """

    @classmethod
    def process_nfe_workbench(
        cls,
        xml_content: str,
        company_profile: CompanyFiscalProfile,
        reference_date: date,
        available_rules: List[FiscalTaxRule]
    ) -> WorkbenchNFeDocument:
        nfe_id = f"nfe_wb_{uuid.uuid4().hex[:8]}"

        # 1. Validação temporal do perfil fiscal da empresa
        if not company_profile.is_valid_at(reference_date):
            raw_hash = hashlib.sha256(xml_content.encode("utf-8")).hexdigest()
            return WorkbenchNFeDocument(
                nfe_id=nfe_id,
                company_id=company_profile.company_id,
                access_key="00000000000000000000000000000000000000000000",
                raw_xml_hash=raw_hash,
                issue_date=reference_date,
                reference_date=reference_date,
                nfe_state=NFeLifecycleState.VALIDATION_FAILED,
                total_invoice_amount=Decimal("0.00"),
                total_tax_amount=Decimal("0.00"),
                tax_totals_by_type={},
                items=[],
                master_decision_id=f"dec_invalid_{nfe_id}",
                review_required=True,
                document_hash=raw_hash
            )

        # 2. Executa a análise End-to-End via NFeAnalysisPipeline
        xml_bytes = xml_content.encode("utf-8")
        analysis: NFeAnalysisResult = NFeAnalysisPipeline.analyze_nfe_xml(
            xml_bytes=xml_bytes,
            company_id=company_profile.company_id,
            reference_date=reference_date,
            available_rules=available_rules
        )

        wb_items: List[WorkbenchItemDetail] = []
        for item_res in analysis.item_results:
            p_state = ProductLifecycleState.CLASSIFIED if not item_res.review_required else ProductLifecycleState.HUMAN_REVIEW
            d_state = DecisionLifecycleState.CONFIRMED if not item_res.review_required else DecisionLifecycleState.HUMAN_REVIEW

            wb_items.append(WorkbenchItemDetail(
                item_index=item_res.item_index,
                product_code=item_res.product_code,
                product_description=item_res.product_description,
                ncm=item_res.ncm,
                cest=item_res.cest,
                xml_cst=item_res.xml_cst,
                xml_cfop=item_res.xml_cfop,
                calculated_cst=item_res.calculated_cst,
                calculated_cfop=item_res.calculated_cfop,
                item_tax_total=item_res.item_tax_total,
                product_state=p_state,
                decision_state=d_state,
                decision_id=item_res.decision_id
            ))

        nfe_state = NFeLifecycleState.PROCESSED if not analysis.review_required else NFeLifecycleState.HUMAN_REVIEW

        return WorkbenchNFeDocument(
            nfe_id=nfe_id,
            company_id=company_profile.company_id,
            access_key=analysis.access_key,
            raw_xml_hash=analysis.raw_xml_hash,
            issue_date=analysis.issue_date,
            reference_date=reference_date,
            nfe_state=nfe_state,
            total_invoice_amount=analysis.total_invoice_amount,
            total_tax_amount=analysis.total_tax_amount,
            tax_totals_by_type=analysis.tax_totals_by_type,
            items=wb_items,
            master_decision_id=analysis.master_decision_id,
            review_required=analysis.review_required,
            document_hash=analysis.analysis_hash
        )
