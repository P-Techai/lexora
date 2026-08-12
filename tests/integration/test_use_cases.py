from datetime import date, datetime
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.application.dto.ingestion_dto import IngestionStatus, LegalDocumentIngestionRequest
from src.application.ports.structure_parser import SyntheticLegalStructureParser
from src.application.use_cases.legal.ingest_document import IngestDocumentUseCase
from src.domain.entities.source import Source
from src.domain.enums import DocumentType, Jurisdiction
from src.infrastructure.db.base import Base
from src.infrastructure.db.repositories.postgres_repositories import (
    PostgresLegalDocumentRepository,
    PostgresLegalNodeRepository,
    PostgresLegalVersionRepository,
    PostgresSourceRepository,
)

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_idempotency_and_dry_run(test_session: AsyncSession):
    source_repo = PostgresSourceRepository(test_session)
    doc_repo = PostgresLegalDocumentRepository(test_session)
    version_repo = PostgresLegalVersionRepository(test_session)
    node_repo = PostgresLegalNodeRepository(test_session)
    parser = SyntheticLegalStructureParser()

    # Inserir Source obrigatório
    source = Source(id="src-planalto", name="Planalto", authority_level=1)
    await source_repo.save(source)

    use_case = IngestDocumentUseCase(
        source_repo=source_repo,
        doc_repo=doc_repo,
        version_repo=version_repo,
        node_repo=node_repo,
        structure_parser=parser
    )

    req = LegalDocumentIngestionRequest(
        source_id="src-planalto",
        document_type=DocumentType.ORDINARY_LAW,
        document_number="9999",
        title="Lei Sintética de Teste 9999",
        ementa="Ementa da lei de teste",
        jurisdiction=Jurisdiction.FEDERAL,
        issuing_body="PRESIDENCIA",
        publication_date=date(2026, 1, 1),
        raw_content="Art. 1º Texto original da lei sintética."
    )

    # 1. Testar Dry Run (não deve gravar nada)
    dry_res = await use_case.execute(req, dry_run=True)
    assert dry_res.status == IngestionStatus.CREATED
    assert "DRY RUN" in dry_res.warnings[0]
    assert await doc_repo.get_by_id(dry_res.document_id or "") is None

    # 2. Primeira ingestão real: Status CREATED
    res1 = await use_case.execute(req, dry_run=False)
    assert res1.status == IngestionStatus.CREATED
    assert res1.created is True
    assert res1.duplicate is False
    assert res1.document_id is not None

    # 3. Segunda ingestão idêntica: Status DUPLICATE (Idempotência)
    res2 = await use_case.execute(req, dry_run=False)
    assert res2.status == IngestionStatus.DUPLICATE
    assert res2.duplicate is True
    assert res2.document_id == res1.document_id


@pytest.mark.asyncio
async def test_versioning_on_content_change(test_session: AsyncSession):
    source_repo = PostgresSourceRepository(test_session)
    doc_repo = PostgresLegalDocumentRepository(test_session)
    version_repo = PostgresLegalVersionRepository(test_session)
    node_repo = PostgresLegalNodeRepository(test_session)
    parser = SyntheticLegalStructureParser()

    await source_repo.save(Source(id="src-planalto", name="Planalto", authority_level=1))

    use_case = IngestDocumentUseCase(
        source_repo=source_repo,
        doc_repo=doc_repo,
        version_repo=version_repo,
        node_repo=node_repo,
        structure_parser=parser
    )

    req1 = LegalDocumentIngestionRequest(
        source_id="src-planalto",
        document_type=DocumentType.ORDINARY_LAW,
        document_number="8888",
        title="Lei 8888",
        issuing_body="PRESIDENCIA",
        raw_content="Art. 1º Redação original 1990."
    )

    res1 = await use_case.execute(req1)
    assert res1.status == IngestionStatus.CREATED

    # Segunda ingestão da mesma lei com alteração de redação -> Nova versão
    req2 = LegalDocumentIngestionRequest(
        source_id="src-planalto",
        document_type=DocumentType.ORDINARY_LAW,
        document_number="8888",
        title="Lei 8888",
        issuing_body="PRESIDENCIA",
        raw_content="Art. 1º Redação alterada em 2026."
    )

    res2 = await use_case.execute(req2)
    assert res2.status == IngestionStatus.UPDATED
    assert res2.document_id == res1.document_id
    assert res2.version_id != res1.version_id
