"""Phase 8 Real Fiscal Knowledge & Batch NFe Migration

Revision ID: 0012_real_fiscal_knowledge_batch_nfe
Revises: 0011_nfe_operational_fiscal_engine
Create Date: 2026-08-14 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0012_real_fiscal_knowledge_batch_nfe'
down_revision: Union[str, None] = '0011_nfe_operational_fiscal_engine'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. fiscal_rule_catalog
    op.create_table(
        'fiscal_rule_catalog',
        sa.Column('rule_id', sa.String(length=64), nullable=False),
        sa.Column('version', sa.String(length=16), nullable=False, server_default='1.0'),
        sa.Column('valid_from', sa.Date(), nullable=False),
        sa.Column('valid_until', sa.Date(), nullable=True),
        sa.Column('jurisdiction', sa.String(length=32), nullable=False),
        sa.Column('tax_type', sa.String(length=16), nullable=False),
        sa.Column('state', sa.String(length=2), nullable=True),
        sa.Column('municipality', sa.String(length=64), nullable=True),
        sa.Column('rate', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('evidence_id', sa.String(length=64), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('rule_id')
    )
    op.create_index('idx_rule_catalog_tax_state', 'fiscal_rule_catalog', ['tax_type', 'state', 'valid_from'])

    # 2. fiscal_nfe_batches
    op.create_table(
        'fiscal_nfe_batches',
        sa.Column('batch_id', sa.String(length=64), nullable=False),
        sa.Column('company_id', sa.String(length=64), nullable=False),
        sa.Column('reference_date', sa.Date(), nullable=False),
        sa.Column('total_xmls', sa.Numeric(precision=6, scale=0), nullable=False, server_default='0'),
        sa.Column('processed_count', sa.Numeric(precision=6, scale=0), nullable=False, server_default='0'),
        sa.Column('failed_count', sa.Numeric(precision=6, scale=0), nullable=False, server_default='0'),
        sa.Column('review_required_count', sa.Numeric(precision=6, scale=0), nullable=False, server_default='0'),
        sa.Column('total_batch_gross_amount', sa.Numeric(precision=18, scale=4), nullable=False, server_default='0'),
        sa.Column('total_batch_tax_amount', sa.Numeric(precision=18, scale=4), nullable=False, server_default='0'),
        sa.Column('batch_status', sa.String(length=32), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('batch_id')
    )
    op.create_index('idx_batches_company_date', 'fiscal_nfe_batches', ['company_id', 'reference_date'])

    # 3. fiscal_batch_items
    op.create_table(
        'fiscal_batch_items',
        sa.Column('item_id', sa.String(length=64), nullable=False),
        sa.Column('batch_id', sa.String(length=64), nullable=False),
        sa.Column('item_index', sa.Numeric(precision=6, scale=0), nullable=False),
        sa.Column('access_key', sa.String(length=44), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['batch_id'], ['fiscal_nfe_batches.batch_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('item_id')
    )
    op.create_index('idx_batch_items_batch', 'fiscal_batch_items', ['batch_id', 'status'])


def downgrade() -> None:
    op.drop_table('fiscal_batch_items')
    op.drop_table('fiscal_nfe_batches')
    op.drop_table('fiscal_rule_catalog')
