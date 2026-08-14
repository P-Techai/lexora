from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DecisionReason(BaseModel):
    """
    Justificativa detalhada de uma decisão ou alerta.
    """
    model_config = ConfigDict(frozen=True)

    reason_id: str = Field(..., description="ID da justificativa")
    code: str = Field(..., description="Código funcional da justificativa (ex.: NO_RULE_FOUND, EXPIRED_RULE, NCM_UNKNOWN)")
    description: str = Field(..., description="Explicação textual humanizada")
    legal_node_id: Optional[str] = Field(None, description="Dispositivo legal associado")
    severity: str = Field(default="INFO", description="Severidade (INFO, WARNING, ERROR, CRITICAL)")
