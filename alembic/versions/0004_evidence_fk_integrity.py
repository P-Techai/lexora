"""Evidence Foreign Key Integrity Migration - Enforce ON DELETE RESTRICT on Evidence FKs

Revision ID: 0004_evidence_fk_integrity
Revises: 0003_legal_integrity_hardening
Create Date: 2026-08-12 02:15:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0004_evidence_fk_integrity'
down_revision: Union[str, None] = '0003_legal_integrity_hardening'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ajuste de FKs na tabela evidences: altera de SET NULL para RESTRICT
    with op.batch_alter_table('evidences', schema=None) as batch_op:
        batch_op.drop_constraint('evidences_legal_document_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('evidences_legal_version_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('evidences_legal_node_id_fkey', type_='foreignkey')
        
        batch_op.create_foreign_key(
            'fk_evidences_legal_document_id',
            'legal_documents',
            ['legal_document_id'],
            ['id'],
            ondelete='RESTRICT'
        )
        batch_op.create_foreign_key(
            'fk_evidences_legal_version_id',
            'legal_versions',
            ['legal_version_id'],
            ['id'],
            ondelete='RESTRICT'
        )
        batch_op.create_foreign_key(
            'fk_evidences_legal_node_id',
            'legal_nodes',
            ['legal_node_id'],
            ['id'],
            ondelete='RESTRICT'
        )


def downgrade() -> None:
    # Operação inversa determinística
    with op.batch_alter_table('evidences', schema=None) as batch_op:
        batch_op.drop_constraint('fk_evidences_legal_node_id', type_='foreignkey')
        batch_op.drop_constraint('fk_evidences_legal_version_id', type_='foreignkey')
        batch_op.drop_constraint('fk_evidences_legal_document_id', type_='foreignkey')
        
        batch_op.create_foreign_key(
            'evidences_legal_node_id_fkey',
            'legal_nodes',
            ['legal_node_id'],
            ['id'],
            ondelete='SET NULL'
        )
        batch_op.create_foreign_key(
            'evidences_legal_version_id_fkey',
            'legal_versions',
            ['legal_version_id'],
            ['id'],
            ondelete='SET NULL'
        )
        batch_op.create_foreign_key(
            'evidences_legal_document_id_fkey',
            'legal_documents',
            ['legal_document_id'],
            ['id'],
            ondelete='SET NULL'
        )
