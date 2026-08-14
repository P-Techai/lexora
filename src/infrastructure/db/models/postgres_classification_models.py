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


class FiscalProductProfileModel(Base):
    """Modelo ORM para perfis cadastrais fiscais de produtos."""
    __tablename__ = "fiscal_product_profiles"

    product_id = Column(String(64), primary_key=True)
    sku = Column(String(64), nullable=True, index=True)
    gtin = Column(String(32), nullable=True, index=True)
    description = Column(Text, nullable=False)
    normalized_description = Column(Text, nullable=False)
    ncm = Column(String(10), nullable=True, index=True)
    cest = Column(String(10), nullable=True, index=True)
    unit = Column(String(10), nullable=False, default="UN")
    origin = Column(String(2), nullable=False, default="0")
    fiscal_status = Column(String(32), nullable=False, index=True)
    classification_confidence = Column(Numeric(5, 4), nullable=False, default=1.0)
    classification_source = Column(String(64), nullable=False, default="DOCUMENT_ORIGIN")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class FiscalCalculationMemoryModel(Base):
    """Modelo ORM para memórias de cálculo tributário (Append-Only)."""
    __tablename__ = "fiscal_calculation_memories"

    calculation_id = Column(String(64), primary_key=True)
    operation_id = Column(String(64), nullable=False, index=True)
    item_id = Column(String(64), nullable=False, index=True)
    tax_type = Column(String(16), nullable=False, index=True)
    taxable_base = Column(Numeric(18, 4), nullable=False)
    rate = Column(Numeric(10, 4), nullable=False)
    calculated_amount = Column(Numeric(18, 4), nullable=False)
    inputs = Column(JSONB, nullable=False)
    formula = Column(Text, nullable=False)
    rounding_policy = Column(String(32), nullable=False, default="ROUND_HALF_UP")
    rule_id = Column(String(64), nullable=True, index=True)
    legal_reference = Column(Text, nullable=True)
    evidence_id = Column(String(64), nullable=True, index=True)
    calculated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    memory_hash = Column(String(64), nullable=False, index=True)


class FiscalDocumentResultModel(Base):
    """Modelo ORM para resultados consolidados de documentos fiscais."""
    __tablename__ = "fiscal_document_results"

    document_id = Column(String(64), primary_key=True)
    company_id = Column(String(64), nullable=False, index=True)
    operation_date = Column(Date, nullable=False, index=True)
    items = Column(JSONB, nullable=False)
    total_gross_amount = Column(Numeric(18, 4), nullable=False)
    total_tax_amount = Column(Numeric(18, 4), nullable=False)
    tax_totals_by_type = Column(JSONB, nullable=False)
    decision_id = Column(
        String(64),
        ForeignKey("fiscal_decisions.decision_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    review_required = Column(String(10), nullable=False, default="false")
    engine_name = Column(String(64), nullable=False)
    engine_version = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class FiscalReprocessingRunModel(Base):
    """Modelo ORM para reprocessamentos históricos sem alteração destrutiva."""
    __tablename__ = "fiscal_reprocessing_runs"

    reprocessing_id = Column(String(64), primary_key=True)
    source_decision_id = Column(
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
    old_engine_version = Column(String(64), nullable=False)
    new_engine_version = Column(String(64), nullable=False)
    reason = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
