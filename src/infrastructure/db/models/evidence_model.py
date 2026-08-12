from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class EvidenceModel(Base):
    __tablename__ = "evidences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False)
    legal_document_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("legal_documents.id", ondelete="SET NULL"), nullable=True
    )
    legal_version_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("legal_versions.id", ondelete="SET NULL"), nullable=True
    )
    legal_node_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("legal_nodes.id", ondelete="SET NULL"), nullable=True
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    quote_or_excerpt: Mapped[str] = mapped_column(Text, nullable=False)
    locator: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    captured_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_evidence_hash", "content_hash"),
        Index("idx_evidence_source_node", "source_id", "legal_node_id"),
    )
