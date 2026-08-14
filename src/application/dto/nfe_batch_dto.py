from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field

from src.domain.fiscal.nfe_batch_pipeline import BatchItemStatus, BatchStatus


class NFeBatchRequest(BaseModel):
    company_id: str = Field(..., description="ID da empresa proprietária do lote")
    reference_date: date = Field(..., description="Data de referência temporal YYYY-MM-DD")
    xml_payloads: List[str] = Field(..., description="Lista de strings UTF-8 contendo os XMLs das NF-es")


class NFeBatchResponse(BaseModel):
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
