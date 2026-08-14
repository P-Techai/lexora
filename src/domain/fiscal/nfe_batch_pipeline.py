import uuid
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.domain.fiscal.nfe_analysis_pipeline import NFeAnalysisPipeline, NFeAnalysisResult


class BatchStatus(str, Enum):
    RECEIVED = "RECEIVED"
    VALIDATING = "VALIDATING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    PARTIAL = "PARTIAL"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


class BatchItemStatus(BaseModel):
    model_config = ConfigDict(frozen=True)

    item_index: int
    filename: Optional[str] = None
    access_key: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    analysis_result: Optional[NFeAnalysisResult] = None


class NFeBatchResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    batch_id: str
    company_id: str
    reference_date: date
    total_xmls: int
    processed_count: int
    failed_count: int
    review_required_count: int
    total_batch_gross_amount: Decimal
    total_batch_tax_amount: Decimal
    batch_status: BatchStatus
    items: List[BatchItemStatus]


class NFeBatchPipeline:
    """
    Pipeline de processamento em lote resiliente para múltiplos XMLs de NF-e.
    """

    @classmethod
    def process_batch(
        cls,
        xml_payloads: List[str],
        company_id: str,
        reference_date: date,
        available_rules: List[FiscalTaxRule],
        batch_id: Optional[str] = None
    ) -> NFeBatchResult:
        b_id = batch_id or f"batch_{uuid.uuid4().hex[:8]}"

        items: List[BatchItemStatus] = []
        processed_count = 0
        failed_count = 0
        review_count = 0
        total_gross = Decimal("0.00")
        total_tax = Decimal("0.00")

        seen_keys = set()

        for idx, xml_str in enumerate(xml_payloads, start=1):
            try:
                xml_bytes = xml_str.encode("utf-8")
                res = NFeAnalysisPipeline.analyze_nfe_xml(
                    xml_bytes=xml_bytes,
                    company_id=company_id,
                    reference_date=reference_date,
                    available_rules=available_rules
                )

                if res.access_key in seen_keys:
                    items.append(BatchItemStatus(
                        item_index=idx,
                        access_key=res.access_key,
                        status="DUPLICATE",
                        error_message="NF-e duplicada no lote"
                    ))
                    failed_count += 1
                    continue

                seen_keys.add(res.access_key)
                processed_count += 1
                total_gross += res.total_invoice_amount
                total_tax += res.total_tax_amount

                if res.review_required:
                    review_count += 1

                items.append(BatchItemStatus(
                    item_index=idx,
                    access_key=res.access_key,
                    status="SUCCESS",
                    analysis_result=res
                ))

            except Exception as e:
                failed_count += 1
                items.append(BatchItemStatus(
                    item_index=idx,
                    status="ERROR",
                    error_message=str(e)
                ))

        if failed_count == 0 and review_count == 0:
            final_status = BatchStatus.COMPLETED
        elif processed_count > 0 and (failed_count > 0 or review_count > 0):
            final_status = BatchStatus.PARTIAL if failed_count > 0 else BatchStatus.REQUIRES_REVIEW
        else:
            final_status = BatchStatus.FAILED

        return NFeBatchResult(
            batch_id=b_id,
            company_id=company_id,
            reference_date=reference_date,
            total_xmls=len(xml_payloads),
            processed_count=processed_count,
            failed_count=failed_count,
            review_required_count=review_count,
            total_batch_gross_amount=total_gross,
            total_batch_tax_amount=total_tax,
            batch_status=final_status,
            items=items
        )
