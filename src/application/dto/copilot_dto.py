from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from src.domain.enums import ReviewReason, ReviewStatus


class DashboardSummaryResponse(BaseModel):
    total_decisions: int = Field(..., description="Total de decisões registradas")
    approved_count: int = Field(..., description="Decisões aprovadas")
    review_required_count: int = Field(..., description="Decisões pendentes de revisão")
    conflict_count: int = Field(..., description="Decisões com conflito normativo")
    no_applicable_rule_count: int = Field(..., description="Decisões sem regra aplicável")
    insufficient_data_count: int = Field(..., description="Decisões com dados insuficientes")
    total_tax_amount_calculated: Decimal = Field(..., description="Total acumulado de tributos calculados")
    open_reviews_count: int = Field(..., description="Revisões em aberto")


class DecisionListItem(BaseModel):
    decision_id: str
    status: str
    company_id: Optional[str] = None
    ncm: str
    total_value: Decimal
    tax_count: int
    review_required: bool
    reference_date: date
    decision_hash: str


class ReviewListItem(BaseModel):
    review_id: str
    decision_id: str
    status: ReviewStatus
    reason: ReviewReason
    description: str
    assigned_to: Optional[str] = None
    created_at: str


class ReviewActionRequest(BaseModel):
    actor_id: str = Field(..., description="ID do usuário aprovador/revisor")
    action: str = Field(..., description="Ação realizada (START, APPROVE, REJECT, ESCALATE)")
    reason: str = Field(..., description="Justificativa do usuário")
    evidence_reference: Optional[str] = Field(None, description="Referência à evidência ou documento fornecido")


class ReprocessResponse(BaseModel):
    old_decision_id: str
    new_decision_id: str
    diff: Dict[str, Any]


class CopilotExplainRequest(BaseModel):
    decision_id: str = Field(..., description="ID da decisão a ser explicada")
    context_query: Optional[str] = Field(None, description="Pergunta opcional do usuário")


class CopilotExplainResponse(BaseModel):
    decision_id: str
    status: str
    summary_text: str
    applied_rules_breakdown: List[Dict[str, Any]]
    tax_calculations_breakdown: List[Dict[str, Any]]
    legal_basis_links: List[Dict[str, Any]]
    warnings: List[str]
    conflicts: List[Dict[str, Any]]
    review_required: bool
    decision_hash: str
