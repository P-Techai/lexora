import os
from datetime import date
from decimal import Decimal
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select

from src.infrastructure.db.models.postgres_nfe_analysis_models import FiscalNFeAnalysisModel

TEST_DB_URL = os.getenv("TEST_DATABASE_URL")


def apply_alembic_migrations(db_url: str):
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")


@pytest.mark.asyncio
async def test_postgres_nfe_analysis_integration():
    if not TEST_DB_URL:
        pytest.skip("TEST_DATABASE_URL não configurada. Pulo do teste de integração PostgreSQL.")

    sync_url = TEST_DB_URL.replace("+asyncpg", "")
    apply_alembic_migrations(sync_url)

    engine = create_async_engine(TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        m = FiscalNFeAnalysisModel(
            analysis_id="an_pg_01",
            access_key="35260812345678000190550010000000011000000018",
            raw_xml_hash="hash_xml_pg_01",
            company_id="comp_pg_01",
            issue_date=date(2026, 8, 14),
            reference_date=date(2026, 8, 14),
            items_count=1,
            total_invoice_amount=Decimal("5000.00"),
            total_tax_amount=Decimal("900.00"),
            tax_totals_by_type={"ICMS": "900.00"},
            review_required="false",
            analysis_hash="hash_an_pg_01"
        )
        session.add(m)
        await session.commit()

        stmt = select(FiscalNFeAnalysisModel).where(FiscalNFeAnalysisModel.analysis_id == "an_pg_01")
        res = await session.execute(stmt)
        fetched = res.scalar_one_or_none()
        assert fetched is not None
        assert fetched.access_key == "35260812345678000190550010000000011000000018"

    await engine.dispose()
