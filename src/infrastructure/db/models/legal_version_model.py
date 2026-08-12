from datetime import date, datetime
from typing import Optional
from sqlalchemy import CheckConstraint, Date, DateTime, Enum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums import VersionStatus
from src.infrastructure.db.base import Base


class LegalVersionModel(Base):
    __tablename__ = "legal_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    legal_document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("legal_documents.id", ondelete="CASCADE"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    published_at: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[VersionStatus] = mapped_column(
        Enum(VersionStatus, native_enum=False), default=VersionStatus.ACTIVE, nullable=False
    )
    source_document_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    raw_storage_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    parser_version: Mapped[str] = mapped_column(String(50), default="1.0.0", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    document: Mapped["LegalDocumentModel"] = relationship("LegalDocumentModel", back_populates="versions")
    nodes: Mapped[list["LegalNodeModel"]] = relationship(
        "LegalNodeModel", back_populates="version", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint(
            "effective_until IS NULL OR effective_from IS NULL OR effective_until >= effective_from",
            name="chk_version_effective_dates"
        ),
        Index("idx_version_doc_ver", "legal_document_id", "version_number", unique=True),
        Index("idx_version_temporal", "legal_document_id", "effective_from", "effective_until", "status"),
        Index("idx_version_hash", "content_hash"),
    )
