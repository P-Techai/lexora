from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB

from src.infrastructure.db.base import Base


class FiscalTaxRuleModel(Base):
    """Modelo ORM para regras tributárias formais."""
    __tablename__ = "fiscal_tax_rules"

    rule_id = Column(String(64), primary_key=True)
    tax_type = Column(String(32), nullable=False, index=True)
    jurisdiction = Column(String(32), nullable=False, index=True)
    state = Column(String(2), nullable=True, index=True)
    municipality = Column(String(64), nullable=True, index=True)
    effective_from = Column(Date, nullable=False, index=True)
    effective_until = Column(Date, nullable=True, index=True)
    priority = Column(Integer, nullable=False, default=100, index=True)
    formula = Column(Text, nullable=False, default="base * rate")
    rate = Column(Numeric(10, 4), nullable=False, default=Decimal("0.0000"))
    base_reduction = Column(Numeric(10, 4), nullable=False, default=Decimal("0.0000"))
    is_exempt = Column(Boolean, nullable=False, default=False)
    has_benefit = Column(Boolean, nullable=False, default=False)
    
    source_legal_node_id = Column(
        String(64),
        ForeignKey("legal_nodes.node_id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )
    source_legal_version_id = Column(
        String(64),
        ForeignKey("legal_versions.version_id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )
    evidence_id = Column(
        String(64),
        ForeignKey("evidences.evidence_id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )
    rule_version = Column(Integer, nullable=False, default=1)
    status = Column(String(32), nullable=False, default="ACTIVE")
    conditions = Column(JSONB, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_fiscal_rules_tax_juris_dates", "tax_type", "jurisdiction", "effective_from", "effective_until"),
    )


class FiscalCalculationLogModel(Base):
    """Modelo ORM para a memória de cálculo imutável."""
    __tablename__ = "fiscal_calculation_logs"

    log_id = Column(String(64), primary_key=True)
    calculation_id = Column(String(64), nullable=False, unique=True, index=True)
    input_hash = Column(String(64), nullable=False, index=True)
    fact_snapshot = Column(JSONB, nullable=False)
    rule_snapshot = Column(JSONB, nullable=False)
    formula = Column(Text, nullable=False)
    base = Column(Numeric(18, 4), nullable=False)
    rate = Column(Numeric(10, 4), nullable=False)
    reduction = Column(Numeric(10, 4), nullable=False)
    result = Column(Numeric(18, 4), nullable=False)
    rounding = Column(Numeric(18, 4), nullable=False, default=Decimal("0.0000"))
    legal_basis = Column(JSONB, nullable=False)
    reference_date = Column(Date, nullable=False, index=True)
    engine_version = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class FiscalDecisionModel(Base):
    """Modelo ORM para decisões tributárias consolidadas."""
    __tablename__ = "fiscal_decisions"

    decision_id = Column(String(64), primary_key=True)
    status = Column(String(32), nullable=False, index=True)
    classification = Column(JSONB, nullable=False)
    tax_results = Column(JSONB, nullable=False)
    applied_rules = Column(JSONB, nullable=False)
    legal_basis = Column(JSONB, nullable=False)
    warnings = Column(JSONB, nullable=False, default=list)
    conflicts = Column(JSONB, nullable=False, default=list)
    review_required = Column(Boolean, nullable=False, default=False, index=True)
    decision_trace = Column(JSONB, nullable=True)
    reference_date = Column(Date, nullable=False, index=True)
    decision_hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class NFeDocumentModel(Base):
    """Modelo ORM para documentos de NFe importados com restrição de duplicidade."""
    __tablename__ = "nfe_documents"

    access_key = Column(String(44), primary_key=True)
    raw_xml_hash = Column(String(64), nullable=False, unique=True, index=True)
    company_id = Column(String(64), nullable=False, index=True)
    issuer_cnpj = Column(String(14), nullable=False, index=True)
    issuer_name = Column(String(255), nullable=False)
    issuer_state = Column(String(2), nullable=False)
    recipient_cnpj = Column(String(14), nullable=False, index=True)
    recipient_name = Column(String(255), nullable=False)
    recipient_state = Column(String(2), nullable=False)
    issue_date = Column(Date, nullable=False, index=True)
    total_invoice_amount = Column(Numeric(18, 4), nullable=False)
    raw_xml_content = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("access_key", name="uq_nfe_documents_access_key"),
    )


class NFeItemModel(Base):
    """Modelo ORM para itens de NFe vinculados com FK RESTRICT."""
    __tablename__ = "nfe_items"

    item_id = Column(String(64), primary_key=True)
    access_key = Column(
        String(44),
        ForeignKey("nfe_documents.access_key", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    item_number = Column(Integer, nullable=False)
    product_code = Column(String(64), nullable=False)
    product_description = Column(Text, nullable=False)
    ncm = Column(String(8), nullable=False, index=True)
    cest = Column(String(7), nullable=True)
    cfop = Column(String(4), nullable=False, index=True)
    uom = Column(String(10), nullable=False)
    quantity = Column(Numeric(18, 4), nullable=False)
    unit_value = Column(Numeric(18, 4), nullable=False)
    total_value = Column(Numeric(18, 4), nullable=False)
    cst_icms = Column(String(3), nullable=True, index=True)
    icms_base = Column(Numeric(18, 4), nullable=False, default=Decimal("0.0000"))
    icms_rate = Column(Numeric(10, 4), nullable=False, default=Decimal("0.0000"))
    icms_amount = Column(Numeric(18, 4), nullable=False, default=Decimal("0.0000"))
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("access_key", "item_number", name="uq_nfe_item_access_key_number"),
    )


class FiscalClassificationModel(Base):
    """Modelo ORM para histórico de classificações fiscais."""
    __tablename__ = "fiscal_classifications"

    classification_id = Column(String(64), primary_key=True)
    ncm = Column(String(8), nullable=False, index=True)
    cst = Column(String(3), nullable=True, index=True)
    cfop = Column(String(4), nullable=True, index=True)
    status = Column(String(32), nullable=False, index=True)
    reasons = Column(JSONB, nullable=False, default=list)
    legal_node_id = Column(
        String(64),
        ForeignKey("legal_nodes.node_id", ondelete="RESTRICT"),
        nullable=True,
        index=True
    )
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
