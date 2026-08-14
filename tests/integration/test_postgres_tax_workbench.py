import os
from datetime import date
from decimal import Decimal
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import select

from src.infrastructure.db.models.postgres_workbench_models import CompanyFiscalProfileModel, WorkbenchNFeDocumentModel

TEST_DB_URL = os.getenv("TEST_DATABASE_URL")


def apply_alembic_migrations(db_url: str):
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")


@pytest.mark.asyncio
async def test_postgres_tax_workbench_integration():
    if not TEST_DB_URL:
        pytest.skip("TEST_DATABASE_URL não configurada. Pulo do teste de integração PostgreSQL.")

    sync_url = TEST_DB_URL.replace("+asyncpg", "")
    apply_alembic_migrations(sync_url)

    engine = create_async_engine(TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        # 1. Salva perfil fiscal da empresa
        comp_m = CompanyFiscalProfileModel(
            company_id="comp_pg_wb_01",
            cnpj="12345678000190",
            corporate_name="EMPRESA TESTE WORKBENCH PG",
            trade_name="WORKBENCH PG",
            state="SP",
            municipality="SAO PAULO",
            tax_regime="LUCRO_REAL",
            valid_from=date(2020, 1, 1)
        )
        session.add(comp_m)

        # 2. Salva documento NF-e no workbench
        doc_m = WorkbenchNFeDocumentModel(
            nfe_id="nfe_pg_wb_01",
            company_id="comp_pg_wb_01",
            access_key="35260812345678000190550010000000011000000018",
            raw_xml_hash="hash_raw_pg_wb_01",
            issue_date=date(2026, 8, 14),
            reference_date=date(2026, 8, 14),
            nfe_state="PROCESSED",
            total_invoice_amount=Decimal("5000.00"),
            total_tax_amount=Decimal("900.00"),
            tax_totals_by_type={"ICMS": "900.00"},
            master_decision_id="dec_pg_wb_01",
            review_required="false",
            document_hash="hash_doc_pg_wb_01"
        )
        session.add(doc_m)
        await session.commit()

        stmt = select(WorkbenchNFeDocumentModel).where(WorkbenchNFeDocumentModel.nfe_id == "nfe_pg_wb_01")
        res = await session.execute(stmt)
        fetched = res.scalar_one_or_none()
        assert fetched is not None
        assert fetched.nfe_state == "PROCESSED"

    await engine.dispose()
