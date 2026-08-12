"""Legal Integrity Hardening Migration - Enforce ON DELETE RESTRICT on all Legal Foreign Keys

Revision ID: 0003_legal_integrity_hardening
Revises: 0002_acquisition_and_artifacts
Create Date: 2026-08-12 02:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0003_legal_integrity_hardening'
down_revision: Union[str, None] = '0002_acquisition_and_artifacts'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Ajuste de FKs na tabela legal_versions
    with op.batch_alter_table('legal_versions', schema=None) as batch_op:
        batch_op.drop_constraint('legal_versions_legal_document_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_legal_versions_legal_document_id',
            'legal_documents',
            ['legal_document_id'],
            ['id'],
            ondelete='RESTRICT'
        )

    # 2. Ajuste de FKs na tabela legal_nodes
    with op.batch_alter_table('legal_nodes', schema=None) as batch_op:
        batch_op.drop_constraint('legal_nodes_legal_version_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('legal_nodes_parent_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_legal_nodes_legal_version_id',
            'legal_versions',
            ['legal_version_id'],
            ['id'],
            ondelete='RESTRICT'
        )
        batch_op.create_foreign_key(
            'fk_legal_nodes_parent_id',
            'legal_nodes',
            ['parent_id'],
            ['id'],
            ondelete='RESTRICT'
        )

    # 3. Ajuste de FKs na tabela legal_relations
    with op.batch_alter_table('legal_relations', schema=None) as batch_op:
        batch_op.drop_constraint('legal_relations_source_node_id_fkey', type_='foreignkey')
        batch_op.drop_constraint('legal_relations_target_node_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_legal_relations_source_node_id',
            'legal_nodes',
            ['source_node_id'],
            ['id'],
            ondelete='RESTRICT'
        )
        batch_op.create_foreign_key(
            'fk_legal_relations_target_node_id',
            'legal_nodes',
            ['target_node_id'],
            ['id'],
            ondelete='RESTRICT'
        )


def downgrade() -> None:
    # Restaura constraints com RESTRICT caso necessário
    pass
