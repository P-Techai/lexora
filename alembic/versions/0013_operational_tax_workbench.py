"""Phase 9 Operational Tax Workbench Migration

Revision ID: 0013_operational_tax_workbench
Revises: 0012_real_fiscal_knowledge_batch_nfe
Create Date: 2026-08-14 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = '0013_operational_tax_workbench'
down_revision: Union[str, None] = '0012_real_fiscal_knowledge_batch_nfe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. fiscal_company_profiles
    op.create_table(
        'fiscal_company_profiles',
        sa.Column('company_id', sa.String(length=64), nullable=False),
        sa.Column('cnpj', sa.String(length=14), nullable=False),
        sa.Column('corporate_name', sa.Text(), nullable=False),
        sa.Column('trade_name', sa.Text(), nullable=True),
        sa.Column('state', sa.String(length=2), nullable=False),
        sa.Column('municipality', sa.String(length=64), nullable=False),
        sa.Column('tax_regime', sa.String(length=32), nullable=False),
        sa.Column('valid_from', sa.Date(), nullable=False),
        sa.Column('valid_until', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('company_id'),
        sa.UniqueConstraint('cnpj', name='uq_company_cnpj')
    )
    op.create_index('idx_company_state_regime', 'fiscal_company_profiles', ['state', 'tax_regime'])

    # 2. fiscal_workbench_nfe_documents
    op.create_table(
        'fiscal_workbench_nfe_documents',
        sa.Column('nfe_id', sa.String(length=64), nullable=False),
        sa.Column('company_id', sa.String(length=64), nullable=False),
        sa.Column('access_key', sa.String(length=44), nullable=False),
        sa.Column('raw_xml_hash', sa.String(length=64), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('reference_date', sa.Date(), nullable=False),
        sa.Column('nfe_state', sa.String(length=32), nullable=False),
        sa.Column('total_invoice_amount', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('total_tax_amount', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('tax_totals_by_type', JSONB(), nullable=False),
        sa.Column('master_decision_id', sa.String(length=64), nullable=False),
        sa.Column('review_required', sa.String(length=10), nullable=False, server_default='false'),
        sa.Column('document_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['company_id'], ['fiscal_company_profiles.company_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('nfe_id'),
        sa.UniqueConstraint('access_key', name='uq_wb_nfe_access_key'),
        sa.UniqueConstraint('raw_xml_hash', name='uq_wb_nfe_raw_xml_hash')
    )
    op.create_index('idx_wb_nfe_company_state', 'fiscal_workbench_nfe_documents', ['company_id', 'nfe_state', 'reference_date'])

    # 3. fiscal_workbench_items
    op.create_table(
        'fiscal_workbench_items',
        sa.Column('item_id', sa.String(length=64), nullable=False),
        sa.Column('nfe_id', sa.String(length=64), nullable=False),
        sa.Column('item_index', sa.Numeric(precision=6, scale=0), nullable=False),
        sa.Column('product_code', sa.String(length=64), nullable=False),
        sa.Column('product_description', sa.Text(), nullable=False),
        sa.Column('ncm', sa.String(length=10), nullable=False),
        sa.Column('cest', sa.String(length=10), nullable=True),
        sa.Column('calculated_cst', sa.String(length=10), nullable=False),
        sa.Column('calculated_cfop', sa.String(length=10), nullable=False),
        sa.Column('item_tax_total', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('product_state', sa.String(length=32), nullable=False),
        sa.Column('decision_state', sa.String(length=32), nullable=False),
        sa.Column('decision_id', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['nfe_id'], ['fiscal_workbench_nfe_documents.nfe_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('item_id')
    )
    op.create_index('idx_wb_items_nfe', 'fiscal_workbench_items', ['nfe_id', 'product_state'])


def downgrade() -> None:
    op.drop_table('fiscal_workbench_items')
    op.drop_table('fiscal_workbench_nfe_documents')
    op.drop_table('fiscal_company_profiles')
