from datetime import date, datetime
from typing import Any, Dict, Optional
from sqlalchemy import CheckConstraint, Date, DateTime, Enum, ForeignKey, Index, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums import LegalNodeType, NodeStatus
from src.infrastructure.db.base import Base


class LegalNodeModel(Base):
    __tablename__ = "legal_nodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    legal_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("legal_versions.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("legal_nodes.id", ondelete="CASCADE"), nullable=True
    )
    node_type: Mapped[LegalNodeType] = mapped_column(Enum(LegalNodeType, native_enum=False), nullable=False)
    identifier: Mapped[str] = mapped_column(String(100), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    path: Mapped[str] = mapped_column(String(1024), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[NodeStatus] = mapped_column(
        Enum(NodeStatus, native_enum=False), default=NodeStatus.ACTIVE, nullable=False
    )
    node_metadata: Mapped[Dict[str, Any]] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    version: Mapped["LegalVersionModel"] = relationship("LegalVersionModel", back_populates="nodes")
    parent: Mapped[Optional["LegalNodeModel"]] = relationship("LegalNodeModel", remote_side=[id], back_populates="children")
    children: Mapped[list["LegalNodeModel"]] = relationship("LegalNodeModel", back_populates="parent", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint(
            "effective_until IS NULL OR effective_from IS NULL OR effective_until >= effective_from",
            name="chk_node_effective_dates"
        ),
        Index("idx_node_version_parent", "legal_version_id", "parent_id", "position"),
        Index("idx_node_type_ident", "node_type", "identifier"),
        Index("idx_node_path", "path"),
        Index("idx_node_hash", "content_hash"),
    )
