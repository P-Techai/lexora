from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import ReviewReason, ReviewStatus


class FiscalReview(BaseModel):
    """
    Entidade representando uma Fila/Item de Revisão Humana de Decisão Fiscal.
    """
    model_config = ConfigDict(frozen=True)

    review_id: str = Field(..., description="ID único do registro de revisão humana")
    decision_id: str = Field(..., description="ID da decisão fiscal associada")
    status: ReviewStatus = Field(default=ReviewStatus.OPEN, description="Status da revisão (OPEN, IN_REVIEW, APPROVED, REJECTED, ESCALATED)")
    reason: ReviewReason = Field(..., description="Motivo estruturado que exigiu revisão humana")
    description: str = Field(..., description="Explicação textual humanizada")
    assigned_to: Optional[str] = Field(None, description="ID do usuário responsável pela revisão")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Data/hora ISO de criação")
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Data/hora ISO da última atualização")


class ReviewEvent(BaseModel):
    """
    Evento de Auditoria Imutável Append-Only representando uma transição ou ação em uma Revisão Humana.
    """
    model_config = ConfigDict(frozen=True)

    event_id: str = Field(..., description="ID único do evento de auditoria")
    review_id: str = Field(..., description="ID da revisão humana")
    decision_id: str = Field(..., description="ID da decisão fiscal associada")
    actor_id: str = Field(..., description="ID do usuário ou agente que realizou a ação")
    action: str = Field(..., description="Ação realizada (START, APPROVE, REJECT, ESCALATE)")
    reason: str = Field(..., description="Justificativa do usuário")
    previous_state: ReviewStatus = Field(..., description="Estado anterior")
    new_state: ReviewStatus = Field(..., description="Novo estado após transição")
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Data/hora ISO do evento")
    evidence_reference: Optional[str] = Field(None, description="Referência a documento ou evidência legal apresentada")
    event_hash: str = Field(..., description="Hash SHA-256 determinístico garantindo imutabilidade do evento")


class HumanOverride(BaseModel):
    """
    Registro de Override Humano preservando intacta a decisão original e gerando nova decisão com override.
    """
    model_config = ConfigDict(frozen=True)

    override_id: str = Field(..., description="ID do override")
    original_decision_id: str = Field(..., description="ID da decisão fiscal original intacta")
    new_decision_id: str = Field(..., description="ID da nova decisão fiscal resultante do override")
    actor_id: str = Field(..., description="ID do usuário autor do override")
    justification: str = Field(..., description="Justificativa técnica/legal do override")
    override_data: Dict[str, Any] = Field(..., description="Dados modificados pelo override (ex: alíquota, CST, NCM)")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(), description="Data/hora ISO")
    override_hash: str = Field(..., description="Hash SHA-256 do override")
