from datetime import date, datetime
from typing import Optional
from sqlalchemy import Date, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums import DocumentType, Jurisdiction
from src.infrastructure.db.base import Base


class LegalDocumentModel(Base):
    __tablename__ = "legal_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("sources.id", ondelete="RESTRICT"), nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(Enum(DocumentType, native_enum=False), nullable=False)
    document_number: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    ementa: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    jurisdiction: Mapped[Jurisdiction] = mapped_column(
        Enum(Jurisdiction, native_enum=False), default=Jurisdiction.FEDERAL, nullable=False
    )
    issuing_body: Mapped[str] = mapped_column(String(255), nullable=False)
    publication_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    official_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    document_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    source: Mapped["SourceModel"] = relationship("SourceModel", back_populates="documents")
    versions: Mapped[list["LegalVersionModel"]] = relationship(
        "LegalVersionModel", back_populates="document", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_legal_doc_lookup", "source_id", "document_type", "document_number", "jurisdiction"),
        Index("idx_legal_doc_pub_date", "publication_date"),
        Index("idx_legal_doc_hash", "document_hash"),
    )
