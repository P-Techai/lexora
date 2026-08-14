from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.domain.enums import ClassificationStatus, CustomerType, InvoicePurpose, OperationType, TaxRegime, TaxType


class ClassifyItemRequest(BaseModel):
    product_description: str = Field(..., description="Descrição comercial do item")
    ncm: Optional[str] = Field(None, description="NCM informado na origem se houver")
    cest: Optional[str] = Field(None, description="CEST informado se houver")
    gtin: Optional[str] = Field(None, description="EAN / GTIN do produto se houver")
    origin: int = Field(default=0, ge=0, le=8, description="Origem da mercadoria")


class ClassifyItemResponse(BaseModel):
    product_id: str
    normalized_description: str
    ncm: str
    cest: Optional[str] = None
    cst: str
    cfop: str
    status: ClassificationStatus
    confidence: float
    source: str


class CalculateItemRequest(BaseModel):
    company_id: str
    tax_regime: TaxRegime
    state: str
    operation_type: OperationType
    operation_date: date
    product_description: str
    quantity: Decimal
    unit_value: Decimal
    total_value: Decimal
    ncm: str
    cest: Optional[str] = None
    cst: Optional[str] = None
    cfop: Optional[str] = None
    origin: int = 0
    customer_type: CustomerType = CustomerType.TAXPAYER
    invoice_purpose: InvoicePurpose = InvoicePurpose.NORMAL


class ProcessDocumentRequest(BaseModel):
    document_id: str
    company_id: str
    operation_date: date
    items: List[CalculateItemRequest]


class ProcessDocumentResponse(BaseModel):
    document_id: str
    company_id: str
    operation_date: date
    items_processed: int
    total_gross_amount: Decimal
    total_tax_amount: Decimal
    tax_totals_by_type: Dict[str, Decimal]
    decision_id: str
    review_required: bool
