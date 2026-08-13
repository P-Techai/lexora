"""Phase 6 Retrieval Migration - Add Legal Node Embeddings Table

Revision ID: 0006_phase6_retrieval
Revises: 0005_phase5_normative_acts
Create Date: 2026-08-13 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0006_phase6_retrieval'
down_revision: Union[str, None] = '0005_phase5_normative_acts'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'legal_node_embeddings',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('legal_node_id', sa.String(length=36), nullable=False),
        sa.Column('legal_version_id', sa.String(length=36), nullable=False),
        sa.Column('legal_document_id', sa.String(length=36), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('embedding_model', sa.String(length=100), nullable=False),
        sa.Column('embedding_model_version', sa.String(length=50), nullable=False),
        sa.Column('dimensions', sa.Integer(), nullable=False),
        sa.Column('vector_data', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['legal_document_id'], ['legal_documents.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['legal_node_id'], ['legal_nodes.id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['legal_version_id'], ['legal_versions.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('legal_node_id', 'content_hash', 'embedding_model', 'embedding_model_version', name='uq_node_embedding_model')
    )
    op.create_index('idx_embedding_document', 'legal_node_embeddings', ['legal_document_id'], unique=False)
    op.create_index('idx_embedding_node', 'legal_node_embeddings', ['legal_node_id'], unique=False)
    op.create_index('idx_embedding_version', 'legal_node_embeddings', ['legal_version_id'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_embedding_version', table_name='legal_node_embeddings')
    op.drop_index('idx_embedding_node', table_name='legal_node_embeddings')
    op.drop_index('idx_embedding_document', table_name='legal_node_embeddings')
    op.drop_table('legal_node_embeddings')
