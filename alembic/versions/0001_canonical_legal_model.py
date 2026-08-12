"""Canonical Legal Data Model Initial Migration

Revision ID: 0001_canonical_legal_model
Revises: 
Create Date: 2026-08-11 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_canonical_legal_model'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Habilitar extensão pgvector se suportada no PostgreSQL
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Tabela sources
    op.create_table(
        'sources',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('official', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('authority_level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('base_url', sa.String(length=1024), nullable=True),
        sa.Column('jurisdiction', sa.String(length=50), nullable=False, server_default='FEDERAL'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('authority_level >= 1 AND authority_level <= 5', name='chk_source_authority_level'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Tabela legal_documents
    op.create_table(
        'legal_documents',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('source_id', sa.String(length=36), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('document_number', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('ementa', sa.Text(), nullable=True),
        sa.Column('jurisdiction', sa.String(length=50), nullable=False, server_default='FEDERAL'),
        sa.Column('issuing_body', sa.String(length=255), nullable=False),
        sa.Column('publication_date', sa.Date(), nullable=True),
        sa.Column('official_url', sa.String(length=1024), nullable=True),
        sa.Column('document_hash', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_legal_doc_lookup', 'legal_documents', ['source_id', 'document_type', 'document_number', 'jurisdiction'])
    op.create_index('idx_legal_doc_pub_date', 'legal_documents', ['publication_date'])
    op.create_index('idx_legal_doc_hash', 'legal_documents', ['document_hash'])

    # 4. Tabela legal_versions
    op.create_table(
        'legal_versions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('legal_document_id', sa.String(length=36), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('published_at', sa.Date(), nullable=True),
        sa.Column('effective_from', sa.Date(), nullable=True),
        sa.Column('effective_until', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('source_document_url', sa.String(length=1024), nullable=True),
        sa.Column('raw_storage_key', sa.String(length=512), nullable=True),
        sa.Column('parser_version', sa.String(length=50), nullable=False, server_default='1.0.0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('effective_until IS NULL OR effective_from IS NULL OR effective_until >= effective_from', name='chk_version_effective_dates'),
        sa.ForeignKeyConstraint(['legal_document_id'], ['legal_documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_version_doc_ver', 'legal_versions', ['legal_document_id', 'version_number'], unique=True)
    op.create_index('idx_version_temporal', 'legal_versions', ['legal_document_id', 'effective_from', 'effective_until', 'status'])
    op.create_index('idx_version_hash', 'legal_versions', ['content_hash'])

    # 5. Tabela legal_nodes
    op.create_table(
        'legal_nodes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('legal_version_id', sa.String(length=36), nullable=False),
        sa.Column('parent_id', sa.String(length=36), nullable=True),
        sa.Column('node_type', sa.String(length=50), nullable=False),
        sa.Column('identifier', sa.String(length=100), nullable=False),
        sa.Column('label', sa.String(length=255), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('normalized_text', sa.Text(), nullable=True),
        sa.Column('path', sa.String(length=1024), nullable=False),
        sa.Column('position', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('effective_from', sa.Date(), nullable=True),
        sa.Column('effective_until', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='ACTIVE'),
        sa.Column('metadata', sa.JSON(), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('effective_until IS NULL OR effective_from IS NULL OR effective_until >= effective_from', name='chk_node_effective_dates'),
        sa.ForeignKeyConstraint(['legal_version_id'], ['legal_versions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['parent_id'], ['legal_nodes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_node_version_parent', 'legal_nodes', ['legal_version_id', 'parent_id', 'position'])
    op.create_index('idx_node_type_ident', 'legal_nodes', ['node_type', 'identifier'])
    op.create_index('idx_node_path', 'legal_nodes', ['path'])
    op.create_index('idx_node_hash', 'legal_nodes', ['content_hash'])

    # 6. Tabela evidences
    op.create_table(
        'evidences',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('source_id', sa.String(length=36), nullable=False),
        sa.Column('legal_document_id', sa.String(length=36), nullable=True),
        sa.Column('legal_version_id', sa.String(length=36), nullable=True),
        sa.Column('legal_node_id', sa.String(length=36), nullable=True),
        sa.Column('source_url', sa.String(length=1024), nullable=True),
        sa.Column('quote_or_excerpt', sa.Text(), nullable=False),
        sa.Column('locator', sa.String(length=255), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('captured_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['legal_document_id'], ['legal_documents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['legal_version_id'], ['legal_versions.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['legal_node_id'], ['legal_nodes.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_evidence_hash', 'evidences', ['content_hash'])
    op.create_index('idx_evidence_source_node', 'evidences', ['source_id', 'legal_node_id'])

    # 7. Tabela legal_relations
    op.create_table(
        'legal_relations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('source_node_id', sa.String(length=36), nullable=False),
        sa.Column('target_node_id', sa.String(length=36), nullable=False),
        sa.Column('relation_type', sa.String(length=50), nullable=False),
        sa.Column('effective_from', sa.Date(), nullable=True),
        sa.Column('effective_until', sa.Date(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('evidence_id', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.CheckConstraint('source_node_id != target_node_id', name='chk_relation_distinct_nodes'),
        sa.CheckConstraint('confidence >= 0.0 AND confidence <= 1.0', name='chk_relation_confidence'),
        sa.ForeignKeyConstraint(['source_node_id'], ['legal_nodes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_node_id'], ['legal_nodes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['evidence_id'], ['evidences.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_relation_source', 'legal_relations', ['source_node_id', 'relation_type'])
    op.create_index('idx_relation_target', 'legal_relations', ['target_node_id', 'relation_type'])


def downgrade() -> None:
    op.drop_index('idx_relation_target', table_name='legal_relations')
    op.drop_index('idx_relation_source', table_name='legal_relations')
    op.drop_table('legal_relations')

    op.drop_index('idx_evidence_source_node', table_name='evidences')
    op.drop_index('idx_evidence_hash', table_name='evidences')
    op.drop_table('evidences')

    op.drop_index('idx_node_hash', table_name='legal_nodes')
    op.drop_index('idx_node_path', table_name='legal_nodes')
    op.drop_index('idx_node_type_ident', table_name='legal_nodes')
    op.drop_index('idx_node_version_parent', table_name='legal_nodes')
    op.drop_table('legal_nodes')

    op.drop_index('idx_version_hash', table_name='legal_versions')
    op.drop_index('idx_version_temporal', table_name='legal_versions')
    op.drop_index('idx_version_doc_ver', table_name='legal_versions')
    op.drop_table('legal_versions')

    op.drop_index('idx_legal_doc_hash', table_name='legal_documents')
    op.drop_index('idx_legal_doc_pub_date', table_name='legal_documents')
    op.drop_index('idx_legal_doc_lookup', table_name='legal_documents')
    op.drop_table('legal_documents')

    op.drop_table('sources')
