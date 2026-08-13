import asyncio
from datetime import date
import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.db.base import Base
from src.infrastructure.db.models.legal_version_model import LegalVersionModel

SQLITE_MEMORY_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def concurrency_session_factory():
    engine = create_async_engine(SQLITE_MEMORY_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    yield session_factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_concurrency_unique_version_constraint_prevents_race_condition(concurrency_session_factory):
    """
    TESTE DE PROTEÇÃO CONTRA CONCORRÊNCIA E RACE CONDITION:
    Provoca tentativa concorrente de inserção de 2 versões com o mesmo (legal_document_id, version_number).
    Garante que o banco de dados impõe a restrição UNIQUE e rejeita a segunda inserção com IntegrityError.
    """
    factory = concurrency_session_factory

    async def insert_version():
        async with factory() as session:
            ver = LegalVersionModel(
                id=f"ver-race-{asyncio.current_task().get_name()}",
                legal_document_id="doc-race-1",
                version_number=1,
                content_hash="hash-race-123",
                effective_from=date(2020, 1, 1)
            )
            session.add(ver)
            await session.commit()

    # Executa as duas inserções simultaneamente
    results = await asyncio.gather(insert_version(), insert_version(), return_exceptions=True)

    # Exatamente uma tarefa deve passar e a outra deve lançar IntegrityError (ou exceção de UNIQUE constraint)
    success_count = sum(1 for r in results if r is None)
    error_count = sum(1 for r in results if isinstance(r, Exception))

    assert success_count == 1, "Exatamente uma inserção de versão concorrente deve ter sucesso."
    assert error_count == 1, "A inserção concorrente duplicada deve ser rejeitada pela Unique Constraint do banco."
