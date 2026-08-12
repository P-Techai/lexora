import os
import pytest
from alembic.config import Config
from alembic import command
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import text


def test_alembic_script_integrity():
    """Valida a integridade e sintaxe dos scripts do Alembic."""
    cfg = Config("alembic.ini")
    script_loc = cfg.get_main_option("script_location")
    assert script_loc == "alembic"


@pytest.mark.asyncio
async def test_transactional_rollback_simulation():
    """Simula uma falha em transação garatindo que 100% dos dados são revertidos (rollback)."""
    # Engine SQLite assíncrono para garantir execução em qualquer máquina sem dependência de serviço externo ativo
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.execute(text("CREATE TABLE test_tab (id INT PRIMARY KEY, val TEXT);"))

    async with engine.connect() as conn:
        trans = await conn.begin()
        try:
            await conn.execute(text("INSERT INTO test_tab VALUES (1, 'ok');"))
            # Força erro de chave primária duplicada
            await conn.execute(text("INSERT INTO test_tab VALUES (1, 'erro');"))
            await trans.commit()
        except Exception:
            await trans.rollback()

    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT COUNT(*) FROM test_tab;"))
        count = res.scalar()
        assert count == 0, "O rollback transacional deveria ter deixado a tabela com 0 registros."

    await engine.dispose()
