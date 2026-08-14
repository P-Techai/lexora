from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import TaxRegime


class CompanyFiscalProfile(BaseModel):
    """
    Perfil fiscal cadastral e temporal da empresa cliente do LÉXORA.
    """
    model_config = ConfigDict(frozen=True)

    company_id: str = Field(..., description="ID único da empresa cliente")
    cnpj: str = Field(..., description="CNPJ de 14 dígitos numéricos")
    corporate_name: str = Field(..., description="Razão Social da empresa")
    trade_name: Optional[str] = Field(None, description="Nome Fantasia")
    state: str = Field(..., description="UF da sede da empresa (ex: SP)")
    municipality: str = Field(..., description="Código IBGE ou nome do município")
    tax_regime: TaxRegime = Field(..., description="Regime Tributário (LUCRO_REAL, LUCRO_PRESUMIDO, SIMPLES_NACIONAL)")
    state_regime: Optional[str] = Field(None, description="Regime Estadual Especial se houver")
    ie: Optional[str] = Field(None, description="Inscrição Estadual")
    im: Optional[str] = Field(None, description="Inscrição Municipal")
    valid_from: date = Field(..., description="Início da vigência temporal da configuração")
    valid_until: Optional[date] = Field(None, description="Fim da vigência temporal da configuração")

    def is_valid_at(self, reference_date: date) -> bool:
        if reference_date < self.valid_from:
            return False
        if self.valid_until and reference_date > self.valid_until:
            return False
        return True
