from datetime import date
import os
import pytest
import pytest_asyncio
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.db.base import Base
from src.infrastructure.db.models.evidence_model import EvidenceModel
from src.infrastructure.db.models.legal_document_model import LegalDocumentModel
from src.infrastructure.db.models.legal_node_model import LegalNodeModel
from src.infrastructure.db.models.legal_version_model import LegalVersionModel
from src.infrastructure.db.models.source_model import SourceModel

# Suporte a ambiente Dual: PostgreSQL como teste autoritativo, SQLite como auxiliar rápido
DEFAULT_TEST_DB_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")


@pytest_asyncio.fixture
async def db_session():
    """Fixture de sessão para teste de integridade referencial em banco de dados."""
    engine = create_async_engine(DEFAULT_TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        # Se for SQLite, habilita PRAGMA foreign_keys = ON
        if "sqlite" in DEFAULT_TEST_DB_URL:
            from sqlalchemy import text
            await conn.execute(text("PRAGMA foreign_keys = ON;"))
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_evidence_referential_integrity_blocks_deletion(db_session: AsyncSession):
    """
    TESTE DE INTEGRIDADE REFERENCIAL DE EVIDÊNCIA EM BANCO DE DADOS REAL:
    Garante que tentar excluir um LegalDocument, LegalVersion ou LegalNode vinculado a uma Evidence
    é REJEITADO com erro de RESTRICT (IntegrityError), impedindo a perda silenciosa da proveniência jurídica.
    """
    source = SourceModel(id="src-1", name="Planalto", base_url="https://planalto.gov.br")
    db_session.add(source)

    doc = LegalDocumentModel(
        id="doc-1", source_id="src-1", document_type="ORDINARY_LAW",
        document_number="100", title="Lei 100", jurisdiction="FEDERAL",
        issuing_body="PRES", publication_date=date(2020, 1, 1), document_hash="h1"
    )
    db_session.add(doc)

    ver = LegalVersionModel(
        id="ver-1", legal_document_id="doc-1", version_number=1,
        content_hash="hv1", effective_from=date(2020, 1, 1)
    )
    db_session.add(ver)

    node = LegalNodeModel(
        id="node-1", legal_version_id="ver-1", node_type="ARTIGO",
        identifier="art-1", label="Art. 1º", text="Texto Art 1",
        path="/art-1", position=1, content_hash="hn1"
    )
    db_session.add(node)

    evidence = EvidenceModel(
        id="ev-1", source_id="src-1", legal_document_id="doc-1",
        legal_version_id="ver-1", legal_node_id="node-1",
        quote_or_excerpt="Evidência oficial", content_hash="he1"
    )
    db_session.add(evidence)
    await db_session.commit()

    # 1. Tentar excluir a LegalDocument referenciada pela Evidence -> Deve falhar com IntegrityError (RESTRICT)
    await db_session.delete(doc)
    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    # 2. Tentar excluir a LegalVersion referenciada pela Evidence -> Deve falhar com IntegrityError (RESTRICT)
    await db_session.delete(ver)
    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()

    # 3. Tentar excluir o LegalNode referenciado pela Evidence -> Deve falhar com IntegrityError (RESTRICT)
    await db_session.delete(node)
    with pytest.raises(IntegrityError):
        await db_session.commit()
