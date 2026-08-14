from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class FiscalCondition(BaseModel):
    """
    Condição individual para filtragem e aplicação de regra fiscal.
    """
    model_config = ConfigDict(frozen=True)

    condition_id: str = Field(..., description="ID da condição")
    field_name: str = Field(..., description="Nome do campo do fato fiscal testado")
    operator: str = Field(..., description="Operador lógico (EQUALS, IN, CONTAINS, NOT_EQUALS)")
    expected_value: Any = Field(..., description="Valor esperado para match")
