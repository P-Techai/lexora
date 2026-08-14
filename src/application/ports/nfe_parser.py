from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class NFeItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    item_number: int = Field(..., description="Número sequencial do item na NFe")
    product_code: str = Field(..., description="Código do produto pelo emitente")
    product_description: str = Field(..., description="Descrição do produto/serviço")
    ncm: str = Field(..., description="Código NCM")
    cest: Optional[str] = Field(None, description="Código CEST")
    cfop: str = Field(..., description="Código CFOP")
    uom: str = Field(..., description="Unidade comercial (UN, KG, L, etc.)")
    quantity: Decimal = Field(..., description="Quantidade comercializada em Decimal")
    unit_value: Decimal = Field(..., description="Valor unitário comercial em Decimal")
    total_value: Decimal = Field(..., description="Valor total bruto do item em Decimal")
    cst_icms: Optional[str] = Field(None, description="CST/CSOSN do ICMS")
    icms_base: Decimal = Field(default=Decimal("0.00"), description="Base do ICMS Decimal")
    icms_rate: Decimal = Field(default=Decimal("0.00"), description="Alíquota do ICMS Decimal")
    icms_amount: Decimal = Field(default=Decimal("0.00"), description="Valor do ICMS Decimal")
    pis_cst: Optional[str] = Field(None, description="CST do PIS")
    pis_amount: Decimal = Field(default=Decimal("0.00"), description="Valor do PIS Decimal")
    cofins_cst: Optional[str] = Field(None, description="CST do COFINS")
    cofins_amount: Decimal = Field(default=Decimal("0.00"), description="Valor do COFINS Decimal")


class NFeDocument(BaseModel):
    model_config = ConfigDict(frozen=True)

    access_key: str = Field(..., description="Chave de acesso com 44 dígitos")
    raw_xml_hash: str = Field(..., description="Hash SHA-256 dos bytes originais do XML")
    issuer_cnpj: str = Field(..., description="CNPJ do emitente")
    issuer_name: str = Field(..., description="Razão social do emitente")
    issuer_state: str = Field(..., description="UF do emitente")
    recipient_cnpj: str = Field(..., description="CNPJ do destinatário")
    recipient_name: str = Field(..., description="Razão social do destinatário")
    recipient_state: str = Field(..., description="UF do destinatário")
    issue_date: date = Field(..., description="Data de emissão da nota fiscal")
    total_invoice_amount: Decimal = Field(..., description="Valor total da NFe Decimal")
    items: List[NFeItem] = Field(default_factory=list, description="Itens da nota fiscal")


class NFeParserPort(ABC):
    """
    Porta abstrata para parsing seguro de arquivos XML de NFe (Nota Fiscal Eletrônica).
    """

    @abstractmethod
    def parse_xml(self, xml_bytes: bytes) -> NFeDocument:
        """
        Realiza o parsing seguro do XML de NFe.
        Protege contra XXE, expansão de entidades (Billion Laughs) e payloads gigantes.
        """
        pass
