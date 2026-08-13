"""Phase 6.1 Vector and Full-Text Search Migration

Revision ID: 0007_phase6_vector_fts
Revises: 0006_phase6_retrieval
Create Date: 2026-08-13 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0007_phase6_vector_fts'
down_revision: Union[str, None] = '0006_phase6_retrieval'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Habilita pgvector se a extensão estiver disponível no PostgreSQL (Neon DB)
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Adiciona coluna tsvector em legal_nodes para FTS nativo do PostgreSQL
    op.add_column('legal_nodes', sa.Column('search_vector', sa.Text(), nullable=True))
    op.create_index('idx_legal_nodes_fts', 'legal_nodes', ['search_vector'], unique=False)


def downgrade() -> None:
    op.drop_index('idx_legal_nodes_fts', table_name='legal_nodes')
    op.drop_column('legal_nodes', 'search_vector')
