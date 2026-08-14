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


class CompanyFiscalProfileModel(Base):
    """Modelo ORM para perfis fiscais de empresas clientes."""
    __tablename__ = "fiscal_company_profiles"

    company_id = Column(String(64), primary_key=True)
    cnpj = Column(String(14), nullable=False, unique=True, index=True)
    corporate_name = Column(Text, nullable=False)
    trade_name = Column(Text, nullable=True)
    state = Column(String(2), nullable=False, index=True)
    municipality = Column(String(64), nullable=False)
    tax_regime = Column(String(32), nullable=False, index=True)
    valid_from = Column(Date, nullable=False, index=True)
    valid_until = Column(Date, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class WorkbenchNFeDocumentModel(Base):
    """Modelo ORM para documentos NF-e no Operational Tax Workbench."""
    __tablename__ = "fiscal_workbench_nfe_documents"

    nfe_id = Column(String(64), primary_key=True)
    company_id = Column(
        String(64),
        ForeignKey("fiscal_company_profiles.company_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    access_key = Column(String(44), nullable=False, unique=True, index=True)
    raw_xml_hash = Column(String(64), nullable=False, unique=True, index=True)
    issue_date = Column(Date, nullable=False, index=True)
    reference_date = Column(Date, nullable=False, index=True)
    nfe_state = Column(String(32), nullable=False, index=True)
    total_invoice_amount = Column(Numeric(18, 4), nullable=False)
    total_tax_amount = Column(Numeric(18, 4), nullable=False)
    tax_totals_by_type = Column(JSONB, nullable=False)
    master_decision_id = Column(String(64), nullable=False, index=True)
    review_required = Column(String(10), nullable=False, default="false")
    document_hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class WorkbenchNFeItemModel(Base):
    """Modelo ORM para itens no Operational Tax Workbench."""
    __tablename__ = "fiscal_workbench_items"

    item_id = Column(String(64), primary_key=True)
    nfe_id = Column(
        String(64),
        ForeignKey("fiscal_workbench_nfe_documents.nfe_id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    item_index = Column(Numeric(6, 0), nullable=False)
    product_code = Column(String(64), nullable=False)
    product_description = Column(Text, nullable=False)
    ncm = Column(String(10), nullable=False, index=True)
    cest = Column(String(10), nullable=True)
    calculated_cst = Column(String(10), nullable=False)
    calculated_cfop = Column(String(10), nullable=False)
    item_tax_total = Column(Numeric(18, 4), nullable=False)
    product_state = Column(String(32), nullable=False)
    decision_state = Column(String(32), nullable=False)
    decision_id = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
