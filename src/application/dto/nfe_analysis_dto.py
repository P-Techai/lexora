from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from src.domain.fiscal.nfe_analysis_pipeline import NFeItemAnalysisResult


class NFeAnalyzeRequest(BaseModel):
    xml_content: str = Field(..., description="Conteúdo string em texto UTF-8 do XML da NF-e")
    company_id: str = Field(..., description="ID da empresa receptora ou emitente")
    reference_date: date = Field(..., description="Data de referência temporal YYYY-MM-DD para avaliação de vigência")


class NFeAnalyzeResponse(BaseModel):
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
