"""Phase 6.3 Fiscal Brain & Decision Engine Migration

Revision ID: 0008_fiscal_brain
Revises: 0007_phase6_vector_fts
Create Date: 2026-08-14 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = '0008_fiscal_brain'
down_revision: Union[str, None] = '0007_phase6_vector_fts'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tabela fiscal_tax_rules
    op.create_table(
        'fiscal_tax_rules',
        sa.Column('rule_id', sa.String(length=64), nullable=False),
        sa.Column('tax_type', sa.String(length=32), nullable=False),
        sa.Column('jurisdiction', sa.String(length=32), nullable=False),
        sa.Column('state', sa.String(length=2), nullable=True),
        sa.Column('municipality', sa.String(length=64), nullable=True),
        sa.Column('effective_from', sa.Date(), nullable=False),
        sa.Column('effective_until', sa.Date(), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('formula', sa.Text(), nullable=False, server_default='base * rate'),
        sa.Column('rate', sa.Numeric(precision=10, scale=4), nullable=False, server_default='0.0000'),
        sa.Column('base_reduction', sa.Numeric(precision=10, scale=4), nullable=False, server_default='0.0000'),
        sa.Column('is_exempt', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('has_benefit', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('source_legal_node_id', sa.String(length=64), nullable=True),
        sa.Column('source_legal_version_id', sa.String(length=64), nullable=True),
        sa.Column('evidence_id', sa.String(length=64), nullable=True),
        sa.Column('rule_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('status', sa.String(length=32), nullable=False, server_default='ACTIVE'),
        sa.Column('conditions', JSONB(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['source_legal_node_id'], ['legal_nodes.node_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['source_legal_version_id'], ['legal_versions.version_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidences.evidence_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('rule_id')
    )
    op.create_index('idx_fiscal_rules_tax_juris_dates', 'fiscal_tax_rules', ['tax_type', 'jurisdiction', 'effective_from', 'effective_until'])
    op.create_index('idx_fiscal_rules_node_id', 'fiscal_tax_rules', ['source_legal_node_id'])

    # 2. Tabela fiscal_calculation_logs
    op.create_table(
        'fiscal_calculation_logs',
        sa.Column('log_id', sa.String(length=64), nullable=False),
        sa.Column('calculation_id', sa.String(length=64), nullable=False),
        sa.Column('input_hash', sa.String(length=64), nullable=False),
        sa.Column('fact_snapshot', JSONB(), nullable=False),
        sa.Column('rule_snapshot', JSONB(), nullable=False),
        sa.Column('formula', sa.Text(), nullable=False),
        sa.Column('base', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('rate', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('reduction', sa.Numeric(precision=10, scale=4), nullable=False),
        sa.Column('result', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('rounding', sa.Numeric(precision=18, scale=4), nullable=False, server_default='0.0000'),
        sa.Column('legal_basis', JSONB(), nullable=False),
        sa.Column('reference_date', sa.Date(), nullable=False),
        sa.Column('engine_version', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('log_id'),
        sa.UniqueConstraint('calculation_id')
    )
    op.create_index('idx_calc_logs_ref_date', 'fiscal_calculation_logs', ['reference_date'])

    # 3. Tabela fiscal_decisions
    op.create_table(
        'fiscal_decisions',
        sa.Column('decision_id', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('classification', JSONB(), nullable=False),
        sa.Column('tax_results', JSONB(), nullable=False),
        sa.Column('applied_rules', JSONB(), nullable=False),
        sa.Column('legal_basis', JSONB(), nullable=False),
        sa.Column('warnings', JSONB(), nullable=False, server_default='[]'),
        sa.Column('conflicts', JSONB(), nullable=False, server_default='[]'),
        sa.Column('review_required', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('decision_trace', JSONB(), nullable=True),
        sa.Column('reference_date', sa.Date(), nullable=False),
        sa.Column('decision_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('decision_id')
    )
    op.create_index('idx_fiscal_decisions_status_ref_date', 'fiscal_decisions', ['status', 'reference_date'])

    # 4. Tabela nfe_documents
    op.create_table(
        'nfe_documents',
        sa.Column('access_key', sa.String(length=44), nullable=False),
        sa.Column('raw_xml_hash', sa.String(length=64), nullable=False),
        sa.Column('company_id', sa.String(length=64), nullable=False),
        sa.Column('issuer_cnpj', sa.String(length=14), nullable=False),
        sa.Column('issuer_name', sa.String(length=255), nullable=False),
        sa.Column('issuer_state', sa.String(length=2), nullable=False),
        sa.Column('recipient_cnpj', sa.String(length=14), nullable=False),
        sa.Column('recipient_name', sa.String(length=255), nullable=False),
        sa.Column('recipient_state', sa.String(length=2), nullable=False),
        sa.Column('issue_date', sa.Date(), nullable=False),
        sa.Column('total_invoice_amount', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('raw_xml_content', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('access_key'),
        sa.UniqueConstraint('raw_xml_hash', name='uq_nfe_documents_raw_xml_hash')
    )
    op.create_index('idx_nfe_docs_company_issue', 'nfe_documents', ['company_id', 'issue_date'])

    # 5. Tabela nfe_items
    op.create_table(
        'nfe_items',
        sa.Column('item_id', sa.String(length=64), nullable=False),
        sa.Column('access_key', sa.String(length=44), nullable=False),
        sa.Column('item_number', sa.Integer(), nullable=False),
        sa.Column('product_code', sa.String(length=64), nullable=False),
        sa.Column('product_description', sa.Text(), nullable=False),
        sa.Column('ncm', sa.String(length=8), nullable=False),
        sa.Column('cest', sa.String(length=7), nullable=True),
        sa.Column('cfop', sa.String(length=4), nullable=False),
        sa.Column('uom', sa.String(length=10), nullable=False),
        sa.Column('quantity', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('unit_value', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('total_value', sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column('cst_icms', sa.String(length=3), nullable=True),
        sa.Column('icms_base', sa.Numeric(precision=18, scale=4), nullable=False, server_default='0.0000'),
        sa.Column('icms_rate', sa.Numeric(precision=10, scale=4), nullable=False, server_default='0.0000'),
        sa.Column('icms_amount', sa.Numeric(precision=18, scale=4), nullable=False, server_default='0.0000'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['access_key'], ['nfe_documents.access_key'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('item_id'),
        sa.UniqueConstraint('access_key', 'item_number', name='uq_nfe_item_access_key_number')
    )
    op.create_index('idx_nfe_items_ncm_cfop', 'nfe_items', ['ncm', 'cfop'])

    # 6. Tabela fiscal_classifications
    op.create_table(
        'fiscal_classifications',
        sa.Column('classification_id', sa.String(length=64), nullable=False),
        sa.Column('ncm', sa.String(length=8), nullable=False),
        sa.Column('cst', sa.String(length=3), nullable=True),
        sa.Column('cfop', sa.String(length=4), nullable=True),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('reasons', JSONB(), nullable=False, server_default='[]'),
        sa.Column('legal_node_id', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['legal_node_id'], ['legal_nodes.node_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('classification_id')
    )


def downgrade() -> None:
    op.drop_table('fiscal_classifications')
    op.drop_table('nfe_items')
    op.drop_table('nfe_documents')
    op.drop_table('fiscal_decisions')
    op.drop_table('fiscal_calculation_logs')
    op.drop_table('fiscal_tax_rules')
