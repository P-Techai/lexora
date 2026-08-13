"""Phase 5 Normative Acts Migration - Add Normative Metadata Indexes and Root Types

Revision ID: 0005_phase5_normative_acts
Revises: 0004_evidence_fk_integrity
Create Date: 2026-08-13 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0005_phase5_normative_acts'
down_revision: Union[str, None] = '0004_evidence_fk_integrity'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Adiciona índice para otimização de busca de atos normativos e proveniência
    with op.batch_alter_table('legal_documents', schema=None) as batch_op:
        batch_op.create_index('idx_legal_doc_number_type', ['document_type', 'document_number', 'jurisdiction'])


def downgrade() -> None:
    # Remoção determinística do índice criado no upgrade
    with op.batch_alter_table('legal_documents', schema=None) as batch_op:
        batch_op.drop_index('idx_legal_doc_number_type')
