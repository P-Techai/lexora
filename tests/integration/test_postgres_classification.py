import os
from decimal import Decimal
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.domain.enums import ClassificationStatus, TaxType
from src.domain.fiscal.calculation_memory import CalculationMemory
from src.domain.fiscal.fiscal_product_profile import FiscalProductProfile
from src.infrastructure.db.repositories.postgres_classification_repositories import PostgresClassificationRepository

TEST_DB_URL = os.getenv("TEST_DATABASE_URL")


def apply_alembic_migrations(db_url: str):
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")


@pytest.mark.asyncio
async def test_postgres_classification_tax_engine_integration():
    if not TEST_DB_URL:
        pytest.skip("TEST_DATABASE_URL não configurada. Pulo do teste de integração PostgreSQL.")

    sync_url = TEST_DB_URL.replace("+asyncpg", "")
    apply_alembic_migrations(sync_url)

    engine = create_async_engine(TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        repo = PostgresClassificationRepository(session)

        # 1. Teste salva e busca perfil de produto
        prof = FiscalProductProfile(
            product_id="prod_pg_01",
            sku="SKU-100",
            gtin="7891234567890",
            description="MONITOR LCD 27",
            normalized_description="MONITOR LCD 27",
            ncm="85285200",
            cest="2100100",
            fiscal_status=ClassificationStatus.CLASSIFIED
        )
        await repo.save_product_profile(prof)
        await session.commit()

        fetched_prof = await repo.get_product_profile_by_id("prod_pg_01")
        assert fetched_prof is not None
        assert fetched_prof.ncm == "85285200"

        # 2. Teste salva e busca memória de cálculo
        mem = CalculationMemory.create(
            calculation_id="calc_pg_01",
            operation_id="op_pg_01",
            item_id="item_pg_01",
            tax_type=TaxType.ICMS,
            taxable_base=Decimal("1000.00"),
            rate=Decimal("18.00"),
            calculated_amount=Decimal("180.00"),
            inputs={"unit_value": "1000.00"},
            formula="taxable_base * rate"
        )
        await repo.save_calculation_memory(mem)
        await session.commit()

        fetched_mem = await repo.get_calculation_memory_by_id("calc_pg_01")
        assert fetched_mem is not None
        assert fetched_mem.calculated_amount == Decimal("180.00")

    await engine.dispose()
