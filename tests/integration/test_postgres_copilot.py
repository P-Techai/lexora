import os
from datetime import date
from decimal import Decimal
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.domain.enums import Jurisdiction, ReviewReason, ReviewStatus, TaxType
from src.domain.fiscal.fiscal_review import FiscalReview
from src.domain.services.fiscal.review_state_machine import ReviewStateMachine
from src.infrastructure.db.models.postgres_fiscal_models import FiscalDecisionModel
from src.infrastructure.db.repositories.postgres_copilot_repositories import PostgresFiscalReviewRepository

TEST_DB_URL = os.getenv("TEST_DATABASE_URL")


def apply_alembic_migrations(db_url: str):
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")


@pytest.mark.asyncio
async def test_postgres_copilot_audit_integration():
    if not TEST_DB_URL:
        pytest.skip("TEST_DATABASE_URL não configurada. Pulo do teste de integração PostgreSQL.")

    sync_url = TEST_DB_URL.replace("+asyncpg", "")
    apply_alembic_migrations(sync_url)

    engine = create_async_engine(TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        # Prepara decisão fake no banco
        dec_model = FiscalDecisionModel(
            decision_id="dec_pg_copilot_01",
            status="REVIEW_REQUIRED",
            classification={"ncm": "84713012"},
            tax_results=[],
            applied_rules=[],
            legal_basis=[],
            warnings=[],
            conflicts=[],
            review_required=True,
            decision_trace={},
            reference_date=date(2026, 6, 1),
            decision_hash="hash_dec_pg_copilot_01"
        )
        session.add(dec_model)
        await session.commit()

        repo = PostgresFiscalReviewRepository(session)
        rev = FiscalReview(
            review_id="rev_pg_01",
            decision_id="dec_pg_copilot_01",
            status=ReviewStatus.OPEN,
            reason=ReviewReason.MISSING_RULE,
            description="Teste PostgreSQL Co-Pilot Audit"
        )
        await repo.save_review(rev)
        await session.commit()

        # Inicia e aprova revisão com transição de estados
        rev_in_review, evt_start = ReviewStateMachine.transition(rev, ReviewStatus.IN_REVIEW, "actor_pg", "START", "Iniciando no PG")
        await repo.save_review(rev_in_review)
        await repo.save_review_event(evt_start)
        await session.commit()

        rev_app, evt_app = ReviewStateMachine.transition(rev_in_review, ReviewStatus.APPROVED, "actor_pg", "APPROVE", "Aprovado no PG")
        await repo.save_review(rev_app)
        await repo.save_review_event(evt_app)
        await session.commit()

        fetched_rev = await repo.get_review_by_id("rev_pg_01")
        assert fetched_rev is not None
        assert fetched_rev.status == ReviewStatus.APPROVED

        events = await repo.list_events_for_review("rev_pg_01")
        assert len(events) == 2
        assert events[0].new_state == ReviewStatus.IN_REVIEW
        assert events[1].new_state == ReviewStatus.APPROVED

    await engine.dispose()
