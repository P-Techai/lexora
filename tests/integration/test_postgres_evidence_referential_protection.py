from datetime import date
import os
import pytest
import pytest_asyncio
from alembic.config import Config
from alembic import command
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.db.models.evidence_model import EvidenceModel
from src.infrastructure.db.models.legal_document_model import LegalDocumentModel
from src.infrastructure.db.models.legal_node_model import LegalNodeModel
from src.infrastructure.db.models.legal_version_model import LegalVersionModel
from src.infrastructure.db.models.source_model import SourceModel

TEST_DB_URL = os.getenv("TEST_DATABASE_URL")


@pytest_asyncio.fixture
async def postgres_db_session():
    """Fixture de sessão obrigatória para PostgreSQL real. Falha se TEST_DATABASE_URL estiver ausente."""
    if not TEST_DB_URL:
        pytest.fail("TEST_DATABASE_URL não configurada! O teste de proteção referencial PostgreSQL exige TEST_DATABASE_URL.")

    if "postgresql" not in TEST_DB_URL:
        pytest.fail(f"TEST_DATABASE_URL deve apontar para PostgreSQL real: '{TEST_DB_URL}'")

    # Aplica as migrations do Alembic no PostgreSQL
    sync_url = TEST_DB_URL.replace("+asyncpg", "")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", sync_url)
    command.upgrade(alembic_cfg, "head")

    engine = create_async_engine(TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_postgres_evidence_referential_integrity_blocks_deletion(postgres_db_session: AsyncSession):
    """
    TESTE COMPORTAMENTAL EM POSTGRESQL REAL:
    Executa no PostgreSQL real sobre schema construído via Alembic migrations.
    Prova que a exclusão de um LegalDocument, LegalVersion ou LegalNode vinculado a uma Evidence
    é fisicamente REJEITADA pelo motor relacional do PostgreSQL com IntegrityError (RESTRICT).
    """
    db_session = postgres_db_session

    source = SourceModel(id="src-pg-1", name="Planalto PG", base_url="https://planalto.gov.br")
    db_session.add(source)

    doc = LegalDocumentModel(
        id="doc-pg-1", source_id="src-pg-1", document_type="ORDINARY_LAW",
        document_number="100", title="Lei 100 PG", jurisdiction="FEDERAL",
        issuing_body="PRES", publication_date=date(2020, 1, 1), document_hash="hpg1"
    )
    db_session.add(doc)

    ver = LegalVersionModel(
        id="ver-pg-1", legal_document_id="doc-pg-1", version_number=1,
        content_hash="hvpg1", effective_from=date(2020, 1, 1)
    )
    db_session.add(ver)

    node = LegalNodeModel(
        id="node-pg-1", legal_version_id="ver-pg-1", node_type="ARTIGO",
        identifier="art-1", label="Art. 1º", text="Texto Art 1 PG",
        path="/art-1", position=1, content_hash="hnpg1"
    )
    db_session.add(node)

    evidence = EvidenceModel(
        id="ev-pg-1", source_id="src-pg-1", legal_document_id="doc-pg-1",
        legal_version_id="ver-pg-1", legal_node_id="node-pg-1",
        quote_or_excerpt="Evidência oficial PG", content_hash="hepg1"
    )
    db_session.add(evidence)
    await db_session.commit()

    # 1. Tentar excluir a LegalDocument referenciada pela Evidence no PostgreSQL -> Rejeitado via RESTRICT
    await db_session.delete(doc)
    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    # 2. Tentar excluir a LegalVersion referenciada pela Evidence no PostgreSQL -> Rejeitado via RESTRICT
    await db_session.delete(ver)
    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    # 3. Tentar excluir o LegalNode referenciado pela Evidence no PostgreSQL -> Rejeitado via RESTRICT
    await db_session.delete(node)
    with pytest.raises(IntegrityError):
        await db_session.commit()
