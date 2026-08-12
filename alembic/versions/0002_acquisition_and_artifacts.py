"""Acquisition and Raw Artifacts Tables Migration

Revision ID: 0002_acquisition_and_artifacts
Revises: 0001_canonical_legal_model
Create Date: 2026-08-11 01:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0002_acquisition_and_artifacts'
down_revision: Union[str, None] = '0001_canonical_legal_model'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tabela raw_artifacts
    op.create_table(
        'raw_artifacts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('source_id', sa.String(length=36), nullable=False),
        sa.Column('url', sa.String(length=1024), nullable=False),
        sa.Column('captured_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('size_bytes', sa.Integer(), nullable=False),
        sa.Column('storage_key', sa.String(length=512), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_artifact_hash', 'raw_artifacts', ['content_hash'])
    op.create_index('idx_artifact_source_url', 'raw_artifacts', ['source_id', 'url'])

    # 2. Tabela acquisition_audit_logs
    op.create_table(
        'acquisition_audit_logs',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('source_id', sa.String(length=36), nullable=False),
        sa.Column('url', sa.String(length=1024), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('content_hash', sa.String(length=64), nullable=True),
        sa.Column('captured_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['source_id'], ['sources.id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_audit_source_time', 'acquisition_audit_logs', ['source_id', 'captured_at'])
    op.create_index('idx_audit_success', 'acquisition_audit_logs', ['success'])


def downgrade() -> None:
    op.drop_index('idx_audit_success', table_name='acquisition_audit_logs')
    op.drop_index('idx_audit_source_time', table_name='acquisition_audit_logs')
    op.drop_table('acquisition_audit_logs')

    op.drop_index('idx_artifact_source_url', table_name='raw_artifacts')
    op.drop_index('idx_artifact_hash', table_name='raw_artifacts')
    op.drop_table('raw_artifacts')
