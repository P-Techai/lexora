from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class LegalNodeModel(Base):
    __tablename__ = "legal_nodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    legal_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("legal_versions.id", ondelete="RESTRICT"), nullable=False
    )
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("legal_nodes.id", ondelete="RESTRICT"), nullable=True
    )
    node_type: Mapped[str] = mapped_column(String(30), nullable=False)
    identifier: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    path: Mapped[str] = mapped_column(String(512), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_node_version_parent", "legal_version_id", "parent_id"),
        Index("idx_node_path", "path"),
        Index("idx_node_type", "node_type"),
    )
