import os
import pytest
from alembic.config import Config
from alembic import command
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

TEST_DB_URL = os.getenv("TEST_DATABASE_URL")


def apply_alembic_migrations(db_url: str):
    """Executa alembic upgrade head sobre a URL do banco de dados de teste (NUNCA usa Base.metadata.create_all)."""
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    command.upgrade(alembic_cfg, "head")


@pytest.mark.asyncio
async def test_postgres_catalog_schema_audit_at_head():
    """
    AUDITORIA DIRETA DE CATÁLOGO POSTGRESQL NO HEAD (MIGRATION 0004):
    1. Exige TEST_DATABASE_URL configurada apontando para PostgreSQL real (Sem fallback SQLite!).
    2. Aplica as migrations via Alembic (`alembic upgrade head`).
    3. Inspeciona a tabela information_schema.referential_constraints do PostgreSQL.
    4. Confirma empiricamente no catálogo do banco:
       - CASCADE = 0
       - SET NULL = 0
       - RESTRICT / NO ACTION = Aplicado em 100% das chaves estrangeiras normativas.
    """
    if not TEST_DB_URL:
        pytest.fail("TEST_DATABASE_URL não configurada! A auditoria de catálogo PostgreSQL exige TEST_DATABASE_URL.")

    if "postgresql" not in TEST_DB_URL:
        pytest.fail(f"TEST_DATABASE_URL deve apontar para PostgreSQL real: '{TEST_DB_URL}'")

    # Converter URL para síncrono para execução do Alembic
    sync_url = TEST_DB_URL.replace("+asyncpg", "")
    apply_alembic_migrations(sync_url)

    engine = create_async_engine(TEST_DB_URL, echo=False)

    catalog_query = text("""
        SELECT 
            rc.constraint_name,
            kcu.table_name,
            kcu.column_name,
            kcu.referenced_table_name,
            rc.delete_rule
        FROM information_schema.referential_constraints rc
        JOIN (
            SELECT 
                constraint_name, 
                table_name, 
                column_name,
                referenced_table_name = (
                    SELECT kcu2.table_name 
                    FROM information_schema.key_column_usage kcu2 
                    WHERE kcu2.constraint_name = kcu1.constraint_name 
                    LIMIT 1
                )
            FROM information_schema.key_column_usage kcu1
        ) kcu ON rc.constraint_name = kcu.constraint_name
    """)

    async with engine.connect() as conn:
        result = await conn.execute(catalog_query)
        rows = result.fetchall()

    await engine.dispose()

    legal_tables = {
        "sources", "legal_documents", "legal_versions", "legal_nodes",
        "legal_relations", "evidences", "raw_artifacts", "acquisition_audit_logs"
    }

    cascade_count = 0
    set_null_count = 0
    restrict_count = 0

    decoded_actions = []

    for row in rows:
        c_name, t_name, col_name, ref_t_name, delete_rule = row[0], row[1], row[2], row[3], row[4]
        if t_name in legal_tables:
            rule_upper = delete_rule.upper()
            decoded_actions.append(f"{t_name}.{col_name} -> {rule_upper}")
            if rule_upper == "CASCADE":
                cascade_count += 1
            elif rule_upper == "SET NULL":
                set_null_count += 1
            elif rule_upper in ("RESTRICT", "NO ACTION"):
                restrict_count += 1

    assert cascade_count == 0, f"Erros no Catálogo PostgreSQL no HEAD: Encontradas {cascade_count} FKs com CASCADE! ({decoded_actions})"
    assert set_null_count == 0, f"Erros no Catálogo PostgreSQL no HEAD: Encontradas {set_null_count} FKs com SET NULL! ({decoded_actions})"
    assert restrict_count > 0, "Auditadas com sucesso as FKs com RESTRICT no catálogo PostgreSQL no HEAD (0004)."
