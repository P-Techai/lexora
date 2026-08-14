from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from src.domain.enums import TaxRegime
from src.domain.fiscal.tax_workbench_pipeline import DecisionLifecycleState, NFeLifecycleState, ProductLifecycleState, WorkbenchItemDetail


class CompanyProfileRequest(BaseModel):
    company_id: str = Field(..., description="ID da empresa cliente")
    cnpj: str = Field(..., description="CNPJ da empresa (14 dígitos)")
    corporate_name: str = Field(..., description="Razão Social")
    trade_name: Optional[str] = Field(None, description="Nome Fantasia")
    state: str = Field(..., description="UF (ex: SP)")
    municipality: str = Field(..., description="Município")
    tax_regime: TaxRegime = Field(..., description="Regime Tributário")
    valid_from: date = Field(..., description="Data inicial de vigência")
    valid_until: Optional[date] = Field(None, description="Data final de vigência se houver")


class CompanyProfileResponse(BaseModel):
    company_id: str
    cnpj: str
    corporate_name: str
    state: str
    municipality: str
    tax_regime: TaxRegime
    valid_from: date
    valid_until: Optional[date] = None


class NFeUploadRequest(BaseModel):
    company_id: str
    reference_date: date
    xml_content: str


class NFeUploadResponse(BaseModel):
    nfe_id: str
    access_key: str
    raw_xml_hash: str
    company_id: str
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
