from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, Field


class DecisionTrace(BaseModel):
    """
    Rastreabilidade e árvore de execução da decisão (DecisionTrace).
    Registra cada etapa: INPUT -> NORMALIZATION -> CLASSIFICATION -> RULE_SELECTION -> TEMPORAL_VALIDATION -> TAX_BASE -> CALCULATION -> LEGAL_VALIDATION -> FINAL_DECISION.
    """
    model_config = ConfigDict(frozen=True)

    trace_id: str = Field(..., description="ID único do trace")
    decision_id: str = Field(..., description="ID da decisão correspondente")
    steps: List[Dict[str, Any]] = Field(default_factory=list, description="Lista ordenada de etapas de execução")
    input_hash: str = Field(..., description="Hash SHA-256 dos dados de entrada")
    rule_snapshot_hash: str = Field(..., description="Hash SHA-256 dos snapshots de regras")
    calculation_hash: str = Field(..., description="Hash SHA-256 dos resultados de cálculos")
