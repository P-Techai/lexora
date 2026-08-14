import os
from datetime import date
from decimal import Decimal
import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.domain.enums import Jurisdiction, TaxType
from src.domain.exceptions import DuplicateNFeError
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.infrastructure.db.models.postgres_fiscal_models import NFeDocumentModel, NFeItemModel
from src.infrastructure.db.repositories.postgres_fiscal_repositories import (
    PostgresFiscalTaxRuleRepository,
    PostgresNFeRepository,
)

TEST_DB_URL = os.getenv("TEST_DATABASE_URL")


def apply_alembic_migrations(db_url: str):
    """Executa alembic upgrade head sobre o banco PostgreSQL de teste."""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")


@pytest.mark.asyncio
async def test_postgres_fiscal_brain_integration():
    """
    Teste de integração do Fiscal Brain no PostgreSQL real (Migration 0008_fiscal_brain).
    Verifica aplicação da migration 0008, idempotência de NFe e persistência de regras fiscais.
    """
    if not TEST_DB_URL:
        pytest.skip("TEST_DATABASE_URL não configurada. Pulo de integração de banco de dados relacional.")

    sync_url = TEST_DB_URL.replace("+asyncpg", "")
    apply_alembic_migrations(sync_url)

    engine = create_async_engine(TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as session:
        rule_repo = PostgresFiscalTaxRuleRepository(session)
        rule = FiscalTaxRule(
            rule_id="rule_pg_test_01",
            tax_type=TaxType.ICMS,
            jurisdiction=Jurisdiction.STATE,
            state="SP",
            effective_from=date(2026, 1, 1),
            rate=Decimal("18.00"),
            base_reduction=Decimal("0.00")
        )
        saved = await rule_repo.save_rule(rule)
        await session.commit()
        assert saved.rule_id == "rule_pg_test_01"

        fetched = await rule_repo.get_rule_by_id("rule_pg_test_01")
        assert fetched is not None
        assert fetched.rate == Decimal("18.00")

        # Teste de Idempotência e Restrição de duplicidade da NFe
        nfe_repo = PostgresNFeRepository(session)
        doc = NFeDocumentModel(
            access_key="35260800000000000000550010000000011000000001",
            raw_xml_hash="hash_xml_nfe_test_01_unique_64_chars_length_hash_sha256_value_01",
            company_id="comp_pg_1",
            issuer_cnpj="11111111000199",
            issuer_name="EMITENTE TESTE",
            issuer_state="SP",
            recipient_cnpj="22222222000188",
            recipient_name="DESTINATARIO TESTE",
            recipient_state="RJ",
            issue_date=date(2026, 5, 10),
            total_invoice_amount=Decimal("1500.00")
        )
        items = [
            NFeItemModel(
                item_id="item_pg_01",
                access_key=doc.access_key,
                item_number=1,
                product_code="PROD_1",
                product_description="PRODUTO TESTE",
                ncm="84713012",
                cfop="5102",
                uom="UN",
                quantity=Decimal("1.00"),
                unit_value=Decimal("1500.00"),
                total_value=Decimal("1500.00")
            )
        ]
        await nfe_repo.save_nfe(doc, items)
        await session.commit()

        # Tentativa de duplicata deve gerar exceção DuplicateNFeError
        doc_dup = NFeDocumentModel(
            access_key="35260800000000000000550010000000011000000001",
            raw_xml_hash="hash_xml_nfe_test_01_unique_64_chars_length_hash_sha256_value_01",
            company_id="comp_pg_1",
            issuer_cnpj="11111111000199",
            issuer_name="EMITENTE TESTE",
            issuer_state="SP",
            recipient_cnpj="22222222000188",
            recipient_name="DESTINATARIO TESTE",
            recipient_state="RJ",
            issue_date=date(2026, 5, 10),
            total_invoice_amount=Decimal("1500.00")
        )
        with pytest.raises(DuplicateNFeError):
            await nfe_repo.save_nfe(doc_dup, [])

    await engine.dispose()
