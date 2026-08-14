from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import CustomerType, InvoicePurpose, OperationType, TaxRegime


class FiscalFact(BaseModel):
    """
    Entidade representando fatos fiscais observados e classificados.
    NÃO aceita verdades fiscais arbitrárias diretamente como fatos.
    """
    model_config = ConfigDict(frozen=True)

    fact_id: str = Field(..., description="ID único do fato fiscal")
    company_id: str = Field(..., description="ID da empresa contribuinte")
    tax_regime: TaxRegime = Field(..., description="Regime tributário da empresa")
    state: str = Field(..., description="UF de origem da operação")
    municipality: Optional[str] = Field(None, description="Código IBGE ou nome do município")
    operation_type: OperationType = Field(..., description="Tipo de operação (INTERNAL, INTERSTATE, IMPORT, EXPORT)")
    operation_date: date = Field(..., description="Data da operação (utilizada para vigência temporal)")
    product_description: str = Field(..., description="Descrição do produto ou serviço")
    quantity: Decimal = Field(..., description="Quantidade negociada")
    unit_value: Decimal = Field(..., description="Valor unitário em Decimal")
    total_value: Decimal = Field(..., description="Valor total da operação em Decimal")
    ncm: Optional[str] = Field(None, description="Código NCM")
    cest: Optional[str] = Field(None, description="Código CEST")
    cfop: Optional[str] = Field(None, description="Código CFOP")
    cst: Optional[str] = Field(None, description="Código CST ou CSOSN")
    origin: int = Field(default=0, ge=0, le=8, description="Origem da mercadoria (0 a 8)")
    customer_type: CustomerType = Field(default=CustomerType.TAXPAYER, description="Perfil do destinatário")
    destination_state: Optional[str] = Field(None, description="UF de destino para operações interestaduais")
    supplier_state: Optional[str] = Field(None, description="UF do fornecedor")
    invoice_purpose: InvoicePurpose = Field(default=InvoicePurpose.NORMAL, description="Finalidade da nota fiscal")
    additional_fields: Dict[str, Any] = Field(default_factory=dict, description="Campos adicionais específicos")
