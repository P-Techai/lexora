from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB

from src.infrastructure.db.base import Base


class FiscalReviewModel(Base):
    """Modelo ORM para a fila e itens de revisão humana."""
    __tablename__ = "fiscal_reviews"

    review_id = Column(String(64), primary_key=True)
    decision_id = Column(
        String(64),
        ForeignKey("fiscal_decisions.decision_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    status = Column(String(32), nullable=False, index=True)
    reason = Column(String(64), nullable=False, index=True)
    description = Column(Text, nullable=False)
    assigned_to = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class FiscalReviewEventModel(Base):
    """Modelo ORM para o log auditável imutável de eventos de revisão (Append-Only)."""
    __tablename__ = "fiscal_review_events"

    event_id = Column(String(64), primary_key=True)
    review_id = Column(
        String(64),
        ForeignKey("fiscal_reviews.review_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    decision_id = Column(
        String(64),
        ForeignKey("fiscal_decisions.decision_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    actor_id = Column(String(64), nullable=False, index=True)
    action = Column(String(32), nullable=False)
    reason = Column(Text, nullable=False)
    previous_state = Column(String(32), nullable=False)
    new_state = Column(String(32), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    evidence_reference = Column(Text, nullable=True)
    event_hash = Column(String(64), nullable=False, index=True)


class FiscalHumanOverrideModel(Base):
    """Modelo ORM para registros de overrides humanos mantendo a decisão original intacta."""
    __tablename__ = "fiscal_human_overrides"

    override_id = Column(String(64), primary_key=True)
    original_decision_id = Column(
        String(64),
        ForeignKey("fiscal_decisions.decision_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    new_decision_id = Column(
        String(64),
        ForeignKey("fiscal_decisions.decision_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    actor_id = Column(String(64), nullable=False, index=True)
    justification = Column(Text, nullable=False)
    override_data = Column(JSONB, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    override_hash = Column(String(64), nullable=False, index=True)
