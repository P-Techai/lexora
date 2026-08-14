from datetime import date
from decimal import Decimal
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field


class TaxCalculationLog(BaseModel):
    """
    Memória de cálculo auditável e imutável de tributos.
    created_at serve como auditoria operacional, NÃO determina a verdade jurídica.
    """
    model_config = ConfigDict(frozen=True)

    log_id: str = Field(..., description="ID único do log de cálculo")
    calculation_id: str = Field(..., description="ID único do cálculo")
    input_hash: str = Field(..., description="Hash SHA-256 dos fatos e dados de entrada")
    fact_snapshot: Dict[str, Any] = Field(..., description="Snapshot imutável do fato fiscal")
    rule_snapshot: Dict[str, Any] = Field(..., description="Snapshot imutável da regra fiscal aplicada")
    formula: str = Field(..., description="Fórmula executada")
    base: Decimal = Field(..., description="Base de cálculo Decimal")
    rate: Decimal = Field(..., description="Alíquota Decimal")
    reduction: Decimal = Field(..., description="Redução de base Decimal")
    result: Decimal = Field(..., description="Resultado final Decimal")
    rounding: Decimal = Field(..., description="Arredondamento Decimal")
    legal_basis: Dict[str, Any] = Field(..., description="Fundamentação legal associada")
    reference_date: date = Field(..., description="Data da operação de referência")
    engine_version: str = Field(..., description="Versão do motor de cálculo")
    created_at: str = Field(..., description="Data/hora ISO de auditoria de criação do log")
