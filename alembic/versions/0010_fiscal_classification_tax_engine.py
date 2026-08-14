"""Phase 6.5 Product Fiscal Classification & Tax Engine Migration

Revision ID: 0010_fiscal_classification_tax_engine
Revises: 0009_fiscal_copilot_audit
Create Date: 2026-08-14 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = '0010_fiscal_classification_tax_engine'
down_revision: Union[str, None] = '0009_fiscal_copilot_audit'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. fiscal_product_profiles
    op.create_table(
        'fiscal_product_profiles',
        sa.Column('product_id', sa.String(length=64), nullable=False),
        sa.Column('sku', sa.String(length=64), nullable=True),
        sa.Column('gtin', sa.String(length=32), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('normalized_description', sa.Text(), nullable=False),
        sa.Column('ncm', sa.String(length=10), nullable=True),
        sa.Column('cest', sa.String(length=10), nullable=True),
        sa.Column('unit', sa.String(length=10), nullable=False, server_default='UN'),
        sa.Column('origin', sa.String(length=2), nullable=False, server_default='0'),
        sa.Column('fiscal_status', sa.String(length=32), nullable=False),
        sa.Column('classification_confidence', sa.Numeric(precision=5, scale=4), nullable=False, server_default='1.0000'),
        sa.Column('classification_source', sa.String(length=64), nullable=False, server_default='DOCUMENT_ORIGIN'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('product_id')
    )
    op.create_index('idx_product_ncm_status', 'fiscal_product_profiles', ['ncm', 'fiscal_status'])

    # 2. fiscal_calculation_memories
    op.create_table(
        'fiscal_calculation_memories',
        sa.Column('calculation_id', sa.String(length=64), nullable=False),
        sa.Column('operation_id', sa.String(length=64), nullable=False),
        sa.Column('item_id', sa.String(length=64), nullable=False),
        sa.Column('tax_type', sa.String(length=16), nullable=False),
        sa.Column('taxable_base', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('rate', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('calculated_amount', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('inputs', JSONB(), nullable=False),
        sa.Column('formula', sa.Text(), nullable=False),
        sa.Column('rounding_policy', sa.String(length=32), nullable=False, server_default='ROUND_HALF_UP'),
        sa.Column('rule_id', sa.String(length=64), nullable=True),
        sa.Column('legal_reference', sa.Text(), nullable=True),
        sa.Column('evidence_id', sa.String(length=64), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('memory_hash', sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint('calculation_id')
    )
    op.create_index('idx_calc_mem_op_item', 'fiscal_calculation_memories', ['operation_id', 'item_id', 'tax_type'])

    # 3. fiscal_document_results
    op.create_table(
        'fiscal_document_results',
        sa.Column('document_id', sa.String(length=64), nullable=False),
        sa.Column('company_id', sa.String(length=64), nullable=False),
        sa.Column('operation_date', sa.Date(), nullable=False),
        sa.Column('items', JSONB(), nullable=False),
        sa.Column('total_gross_amount', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('total_tax_amount', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('tax_totals_by_type', JSONB(), nullable=False),
        sa.Column('decision_id', sa.String(length=64), nullable=False),
        sa.Column('review_required', sa.String(length=10), nullable=False, server_default='false'),
        sa.Column('engine_name', sa.String(length=64), nullable=False),
        sa.Column('engine_version', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['decision_id'], ['fiscal_decisions.decision_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('document_id')
    )
    op.create_index('idx_doc_results_company_date', 'fiscal_document_results', ['company_id', 'operation_date'])

    # 4. fiscal_reprocessing_runs
    op.create_table(
        'fiscal_reprocessing_runs',
        sa.Column('reprocessing_id', sa.String(length=64), nullable=False),
        sa.Column('source_decision_id', sa.String(length=64), nullable=False),
        sa.Column('new_decision_id', sa.String(length=64), nullable=False),
        sa.Column('old_engine_version', sa.String(length=64), nullable=False),
        sa.Column('new_engine_version', sa.String(length=64), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['source_decision_id'], ['fiscal_decisions.decision_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['new_decision_id'], ['fiscal_decisions.decision_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('reprocessing_id')
    )
    op.create_index('idx_reproc_orig_new', 'fiscal_reprocessing_runs', ['source_decision_id', 'new_decision_id'])


def downgrade() -> None:
    op.drop_table('fiscal_reprocessing_runs')
    op.drop_table('fiscal_document_results')
    op.drop_table('fiscal_calculation_memories')
    op.drop_table('fiscal_product_profiles')
