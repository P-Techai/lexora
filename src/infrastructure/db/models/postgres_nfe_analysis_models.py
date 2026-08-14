from datetime import datetime
from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB

from src.infrastructure.db.base import Base


class FiscalNFeAnalysisModel(Base):
    """Modelo ORM para resultados de análises operacionais de NF-e XML."""
    __tablename__ = "fiscal_nfe_analyses"

    analysis_id = Column(String(64), primary_key=True)
    access_key = Column(String(44), nullable=False, unique=True, index=True)
    raw_xml_hash = Column(String(64), nullable=False, unique=True, index=True)
    company_id = Column(String(64), nullable=False, index=True)
    issue_date = Column(Date, nullable=False, index=True)
    reference_date = Column(Date, nullable=False, index=True)
    items_count = Column(Numeric(5, 0), nullable=False, default=1)
    total_invoice_amount = Column(Numeric(18, 4), nullable=False)
    total_tax_amount = Column(Numeric(18, 4), nullable=False)
    tax_totals_by_type = Column(JSONB, nullable=False)
    review_required = Column(String(10), nullable=False, default="false")
    analysis_hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
