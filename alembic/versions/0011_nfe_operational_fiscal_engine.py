"""Phase 7 Operational Fiscal Engine & NFe Migration

Revision ID: 0011_nfe_operational_fiscal_engine
Revises: 0010_fiscal_classification_tax_engine
Create Date: 2026-08-14 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = '0011_nfe_operational_fiscal_engine'
down_revision: Union[str, None] = '0010_fiscal_classification_tax_engine'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. fiscal_nfe_analyses
    op.create_table(
        'fiscal_nfe_analyses',
        sa.Column('analysis_id', sa.String(length=64), nullable=False),
        sa.Column('access_key', sa.String(length=44), nullable=False),
        sa.Column('raw_xml_hash', sa.String(length=64), nullable=False),
        sa.Column('company_id', sa.String(length=64), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('reference_date', sa.Date(), nullable=False),
        sa.Column('items_count', sa.Numeric(precision=5, scale=0), nullable=False, server_default='1'),
        sa.Column('total_invoice_amount', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('total_tax_amount', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('tax_totals_by_type', JSONB(), nullable=False),
        sa.Column('review_required', sa.String(length=10), nullable=False, server_default='false'),
        sa.Column('analysis_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('analysis_id'),
        sa.UniqueConstraint('access_key', name='uq_nfe_analysis_access_key'),
        sa.UniqueConstraint('raw_xml_hash', name='uq_nfe_analysis_raw_xml_hash')
    )
    op.create_index('idx_nfe_analyses_company_date', 'fiscal_nfe_analyses', ['company_id', 'reference_date'])


def downgrade() -> None:
    op.drop_table('fiscal_nfe_analyses')
