"""Phase 6.4 Fiscal Co-Pilot & Audit Dashboard Migration

Revision ID: 0009_fiscal_copilot_audit
Revises: 0008_fiscal_brain
Create Date: 2026-08-14 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = '0009_fiscal_copilot_audit'
down_revision: Union[str, None] = '0008_fiscal_brain'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tabela fiscal_reviews
    op.create_table(
        'fiscal_reviews',
        sa.Column('review_id', sa.String(length=64), nullable=False),
        sa.Column('decision_id', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=32), nullable=False),
        sa.Column('reason', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('assigned_to', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['decision_id'], ['fiscal_decisions.decision_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('review_id')
    )
    op.create_index('idx_fiscal_reviews_status_reason', 'fiscal_reviews', ['status', 'reason'])
    op.create_index('idx_fiscal_reviews_decision', 'fiscal_reviews', ['decision_id'])

    # 2. Tabela fiscal_review_events (Append-Only)
    op.create_table(
        'fiscal_review_events',
        sa.Column('event_id', sa.String(length=64), nullable=False),
        sa.Column('review_id', sa.String(length=64), nullable=False),
        sa.Column('decision_id', sa.String(length=64), nullable=False),
        sa.Column('actor_id', sa.String(length=64), nullable=False),
        sa.Column('action', sa.String(length=32), nullable=False),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.Column('previous_state', sa.String(length=32), nullable=False),
        sa.Column('new_state', sa.String(length=32), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('evidence_reference', sa.Text(), nullable=True),
        sa.Column('event_hash', sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(['review_id'], ['fiscal_reviews.review_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['decision_id'], ['fiscal_decisions.decision_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('event_id')
    )
    op.create_index('idx_review_events_review_hash', 'fiscal_review_events', ['review_id', 'event_hash'])

    # 3. Tabela fiscal_human_overrides
    op.create_table(
        'fiscal_human_overrides',
        sa.Column('override_id', sa.String(length=64), nullable=False),
        sa.Column('original_decision_id', sa.String(length=64), nullable=False),
        sa.Column('new_decision_id', sa.String(length=64), nullable=False),
        sa.Column('actor_id', sa.String(length=64), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('override_data', JSONB(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('override_hash', sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(['original_decision_id'], ['fiscal_decisions.decision_id'], ondelete='RESTRICT'),
        sa.ForeignKeyConstraint(['new_decision_id'], ['fiscal_decisions.decision_id'], ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('override_id')
    )
    op.create_index('idx_overrides_orig_new', 'fiscal_human_overrides', ['original_decision_id', 'new_decision_id'])


def downgrade() -> None:
    op.drop_table('fiscal_human_overrides')
    op.drop_table('fiscal_review_events')
    op.drop_table('fiscal_reviews')
