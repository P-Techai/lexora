import os
from datetime import date
from decimal import Decimal
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select

from src.infrastructure.db.models.postgres_batch_models import FiscalNFeBatchModel, FiscalRuleCatalogModel

TEST_DB_URL = os.getenv("TEST_DATABASE_URL")


def apply_alembic_migrations(db_url: str):
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")


@pytest.mark.asyncio
async def test_postgres_batch_nfe_integration():
    if not TEST_DB_URL:
        pytest.skip("TEST_DATABASE_URL não configurada. Pulo do teste de integração PostgreSQL.")

    sync_url = TEST_DB_URL.replace("+asyncpg", "")
    apply_alembic_migrations(sync_url)

    engine = create_async_engine(TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        # 1. Teste salva regra no catálogo
        rule_m = FiscalRuleCatalogModel(
            rule_id="rule_pg_cat_01",
            version="1.0",
            valid_from=date(2026, 1, 1),
            jurisdiction="STATE",
            tax_type="ICMS",
            state="SP",
            rate=Decimal("18.00"),
            evidence_id="ev_pg_cat_01",
            content_hash="hash_pg_cat_01"
        )
        session.add(rule_m)

        # 2. Teste salva lote de NF-e
        batch_m = FiscalNFeBatchModel(
            batch_id="batch_pg_01",
            company_id="comp_pg_01",
            reference_date=date(2026, 8, 14),
            total_xmls=2,
            processed_count=2,
            failed_count=0,
            review_required_count=0,
            total_batch_gross_amount=Decimal("10000.00"),
            total_batch_tax_amount=Decimal("1800.00"),
            batch_status="COMPLETED"
        )
        session.add(batch_m)
        await session.commit()

        stmt = select(FiscalNFeBatchModel).where(FiscalNFeBatchModel.batch_id == "batch_pg_01")
        res = await session.execute(stmt)
        fetched = res.scalar_one_or_none()
        assert fetched is not None
        assert fetched.batch_status == "COMPLETED"

    await engine.dispose()
