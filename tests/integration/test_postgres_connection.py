from typing import AsyncGenerator
import os
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

TEST_DB_URL = os.getenv("TEST_DATABASE_URL")


@pytest_asyncio_fixture if hasattr(pytest, "asyncio_fixture") else pytest.fixture
def postgres_test_url() -> str:
    if not TEST_DB_URL:
        pytest.fail(
            "TEST_DATABASE_URL não configurada! O teste de conexão PostgreSQL exige TEST_DATABASE_URL apontando para PostgreSQL real."
        )
    if "postgresql" not in TEST_DB_URL:
        pytest.fail(
            f"TEST_DATABASE_URL inválida para PostgreSQL: '{TEST_DB_URL}'. Esperado 'postgresql+asyncpg://...'."
        )
    return TEST_DB_URL


@pytest.mark.asyncio
async def test_postgres_connection_select_version(postgres_test_url: str):
    """
    TESTE DE CONECTIVIDADE POSTGRESQL REAL:
    Conecta ao PostgreSQL fornecido em TEST_DATABASE_URL e executa SELECT version().
    Falha de forma limpa e transparente caso TEST_DATABASE_URL esteja ausente ou não seja PostgreSQL.
    """
    engine = create_async_engine(postgres_test_url, echo=False)
    
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT version();"))
        version_str = result.scalar()

    await engine.dispose()

    assert version_str is not None, "SELECT version() retornou None no PostgreSQL!"
    assert "postgresql" in version_str.lower(), f"O banco de dados conectado não é PostgreSQL: '{version_str}'"
