from datetime import datetime
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB

from src.infrastructure.db.base import Base


class FiscalRuleCatalogModel(Base):
    """Modelo ORM para regras no catálogo fiscal oficial."""
    __tablename__ = "fiscal_rule_catalog"

    rule_id = Column(String(64), primary_key=True)
    version = Column(String(16), nullable=False, default="1.0")
    valid_from = Column(Date, nullable=False, index=True)
    valid_until = Column(Date, nullable=True, index=True)
    jurisdiction = Column(String(32), nullable=False)
    tax_type = Column(String(16), nullable=False, index=True)
    state = Column(String(2), nullable=True, index=True)
    municipality = Column(String(64), nullable=True)
    rate = Column(Numeric(10, 4), nullable=False)
    evidence_id = Column(String(64), nullable=False, index=True)
    content_hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class FiscalNFeBatchModel(Base):
    """Modelo ORM para controle de lotes de processamento de NF-e."""
    __tablename__ = "fiscal_nfe_batches"

    batch_id = Column(String(64), primary_key=True)
    company_id = Column(String(64), nullable=False, index=True)
    reference_date = Column(Date, nullable=False, index=True)
    total_xmls = Column(Numeric(6, 0), nullable=False, default=0)
    processed_count = Column(Numeric(6, 0), nullable=False, default=0)
    failed_count = Column(Numeric(6, 0), nullable=False, default=0)
    review_required_count = Column(Numeric(6, 0), nullable=False, default=0)
    total_batch_gross_amount = Column(Numeric(18, 4), nullable=False, default=0)
    total_batch_tax_amount = Column(Numeric(18, 4), nullable=False, default=0)
    batch_status = Column(String(32), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class FiscalBatchItemModel(Base):
    """Modelo ORM para itens de lotes de processamento de NF-e."""
    __tablename__ = "fiscal_batch_items"

    item_id = Column(String(64), primary_key=True)
    batch_id = Column(
        String(64),
        ForeignKey("fiscal_nfe_batches.batch_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    item_index = Column(Numeric(6, 0), nullable=False)
    access_key = Column(String(44), nullable=True, index=True)
    status = Column(String(32), nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
