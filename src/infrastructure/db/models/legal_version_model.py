from datetime import date, datetime
from typing import Optional
from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class LegalVersionModel(Base):
    __tablename__ = "legal_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    legal_document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("legal_documents.id", ondelete="RESTRICT"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    published_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE", nullable=False)
    source_document_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    raw_storage_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    parser_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("effective_until IS NULL OR effective_from IS NULL OR effective_until >= effective_from", name="chk_version_effective_dates"),
        Index("idx_version_doc_status", "legal_document_id", "status"),
        Index("idx_version_dates", "effective_from", "effective_until"),
        Index("idx_version_hash", "content_hash"),
    )
