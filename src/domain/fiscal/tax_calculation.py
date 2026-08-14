from datetime import date
from decimal import Decimal
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import TaxType


class TaxCalculation(BaseModel):
    """
    Entidade representando o cálculo tributário individual efetuado com precisão Decimal.
    NUNCA utiliza float.
    """
    model_config = ConfigDict(frozen=True)

    tax_type: TaxType = Field(..., description="Tipo do tributo (ICMS, IPI, PIS, COFINS, ISS, etc.)")
    taxable_base: Decimal = Field(..., description="Base de cálculo tributável em Decimal")
    rate: Decimal = Field(..., description="Alíquota aplicada em percentual Decimal")
    base_reduction: Decimal = Field(default=Decimal("0.00"), description="Redução da base de cálculo em Decimal")
    calculated_amount: Decimal = Field(..., description="Valor calculado do tributo em Decimal")
    rounding: Decimal = Field(default=Decimal("0.00"), description="Ajuste de arredondamento em Decimal")
    formula: str = Field(..., description="Fórmula executada no cálculo")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Entradas utilizadas no cálculo")
    rule_id: str = Field(..., description="ID da regra fiscal aplicada")
    legal_basis: Dict[str, Any] = Field(default_factory=dict, description="Referência à fundamentação legal (node, version, evidence)")
    reference_date: date = Field(..., description="Data da operação de referência utilizada")
