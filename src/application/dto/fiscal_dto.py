from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.domain.decision.decision import Decision
from src.domain.enums import CustomerType, DecisionStatus, InvoicePurpose, OperationType, TaxRegime
from src.domain.fiscal.fiscal_classification import FiscalClassification
from src.domain.fiscal.tax_calculation import TaxCalculation


class FiscalFactApiRequest(BaseModel):
    company_id: str = Field(..., description="ID da empresa contribuinte")
    tax_regime: TaxRegime = Field(..., description="Regime tributário da empresa")
    state: str = Field(..., description="UF de origem da operação")
    municipality: Optional[str] = Field(None, description="Município de origem")
    operation_type: OperationType = Field(..., description="Tipo de operação")
    operation_date: date = Field(..., description="Data da operação YYYY-MM-DD")
    product_description: str = Field(..., description="Descrição do produto ou serviço")
    quantity: Decimal = Field(..., description="Quantidade")
    unit_value: Decimal = Field(..., description="Valor unitário Decimal")
    total_value: Decimal = Field(..., description="Valor total da operação Decimal")
    ncm: Optional[str] = Field(None, description="Código NCM")
    cest: Optional[str] = Field(None, description="Código CEST")
    cfop: Optional[str] = Field(None, description="Código CFOP")
    cst: Optional[str] = Field(None, description="Código CST/CSOSN")
    origin: int = Field(default=0, ge=0, le=8, description="Origem da mercadoria (0-8)")
    customer_type: CustomerType = Field(default=CustomerType.TAXPAYER, description="Perfil do cliente")
    destination_state: Optional[str] = Field(None, description="UF de destino")
    supplier_state: Optional[str] = Field(None, description="UF do fornecedor")
    invoice_purpose: InvoicePurpose = Field(default=InvoicePurpose.NORMAL, description="Finalidade da nota fiscal")
    additional_fields: Dict[str, Any] = Field(default_factory=dict, description="Campos adicionais")


class FiscalClassifyResponse(BaseModel):
    classification: FiscalClassification
    normalized_ncm: Optional[str] = None
    normalized_cst: Optional[str] = None
    normalized_cfop: Optional[str] = None


class FiscalCalculateResponse(BaseModel):
    calculations: List[TaxCalculation]
    total_tax_amount: Decimal
    reference_date: date


class FiscalDecisionResponse(BaseModel):
    decision_id: str
    status: DecisionStatus
    classification: FiscalClassification
    tax_results: List[TaxCalculation]
    legal_basis: List[Dict[str, Any]]
    warnings: List[str]
    conflicts: List[Dict[str, Any]]
    review_required: bool
    decision_hash: str
    reference_date: date


class NFeImportRequest(BaseModel):
    xml_content: str = Field(..., description="Conteúdo XML cru da NFe")
    company_id: str = Field(..., description="ID da empresa receptora")


class NFeImportResponse(BaseModel):
    access_key: str
    raw_xml_hash: str
    issuer_cnpj: str
    recipient_cnpj: str
    issue_date: date
    items_count: int
    total_invoice_amount: Decimal
