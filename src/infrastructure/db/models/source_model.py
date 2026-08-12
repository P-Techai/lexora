from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums import Jurisdiction
from src.infrastructure.db.base import Base


class SourceModel(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    official: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    authority_level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    base_url: Mapped[str] = mapped_column(String(1024), nullable=True)
    jurisdiction: Mapped[Jurisdiction] = mapped_column(
        Enum(Jurisdiction, native_enum=False), default=Jurisdiction.FEDERAL, nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    documents: Mapped[list["LegalDocumentModel"]] = relationship(
        "LegalDocumentModel", back_populates="source", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("authority_level >= 1 AND authority_level <= 5", name="chk_source_authority_level"),
    )
