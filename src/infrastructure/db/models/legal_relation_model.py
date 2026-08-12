from datetime import date, datetime
from typing import Optional
from sqlalchemy import CheckConstraint, Date, DateTime, Enum, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.enums import LegalRelationType
from src.infrastructure.db.base import Base


class LegalRelationModel(Base):
    __tablename__ = "legal_relations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_node_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("legal_nodes.id", ondelete="CASCADE"), nullable=False
    )
    target_node_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("legal_nodes.id", ondelete="CASCADE"), nullable=False
    )
    relation_type: Mapped[LegalRelationType] = mapped_column(Enum(LegalRelationType, native_enum=False), nullable=False)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    evidence_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("evidences.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    __table_args__ = (
        CheckConstraint("source_node_id != target_node_id", name="chk_relation_distinct_nodes"),
        CheckConstraint("confidence >= 0.0 AND confidence <= 1.0", name="chk_relation_confidence"),
        Index("idx_relation_source", "source_node_id", "relation_type"),
        Index("idx_relation_target", "target_node_id", "relation_type"),
    )
