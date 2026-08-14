from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import TaxRegime


class CompanyFiscalProfile(BaseModel):
    """
    Perfil cadastral e fiscal da empresa contribuinte.
    Separa estritamente a configuração empresarial da legislação aplicável.
    """
    model_config = ConfigDict(frozen=True)

    company_id: str = Field(..., description="ID único da empresa")
    company_name: str = Field(..., description="Razão social da empresa")
    cnpj: str = Field(..., description="CNPJ limpo com 14 dígitos")
    tax_regime: TaxRegime = Field(..., description="Regime tributário cadastrado")
    state: str = Field(..., description="UF de domicílio fiscal")
    municipality: Optional[str] = Field(None, description="Município de domicílio fiscal")
    ie: Optional[str] = Field(None, description="Inscrição Estadual")
    im: Optional[str] = Field(None, description="Inscrição Municipal")
    special_regimes: List[str] = Field(default_factory=list, description="Regimes especiais de tributação ativas")
    default_operation_settings: Dict[str, Any] = Field(default_factory=dict, description="Configurações padrão de operação")
