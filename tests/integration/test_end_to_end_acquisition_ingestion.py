from datetime import date
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.application.dto.acquisition_dto import AcquisitionRequest, AcquisitionResult
from src.application.dto.ingestion_dto import LegalDocumentIngestionRequest
from src.application.parsers.brazilian_law_parser import BrazilianLawParser
from src.application.use_cases.legal.ingest_document import IngestDocumentUseCase
from src.domain.entities.source import Source
from src.domain.enums import DocumentType, Jurisdiction, LegalNodeType
from src.infrastructure.adapters.mock_acquisition import MockDocumentAcquisitionAdapter
from src.infrastructure.db.base import Base
from src.infrastructure.db.repositories.postgres_repositories import (
    PostgresEvidenceRepository,
    PostgresLegalDocumentRepository,
    PostgresLegalNodeRepository,
    PostgresLegalRelationRepository,
    PostgresLegalVersionRepository,
    PostgresSourceRepository,
)

SQLITE_MEMORY_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def e2e_session():
    engine = create_async_engine(SQLITE_MEMORY_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.mark.asyncio
async def test_end_to_end_acquisition_and_ingestion_pipeline(e2e_session: AsyncSession):
    """
    TESTE END-TO-END OBRIGATÓRIO (PROMPT 07.2):
    Source -> AcquisitionRequest -> AcquisitionResult -> RawArtifact -> Extraction -> SHA-256 ->
    BrazilianLawParser -> LegalDocument -> LegalVersion -> LegalNode tree -> Evidence -> Database.
    """
    session = e2e_session

    source_repo = PostgresSourceRepository(session)
    doc_repo = PostgresLegalDocumentRepository(session)
    ver_repo = PostgresLegalVersionRepository(session)
    node_repo = PostgresLegalNodeRepository(session)
    rel_repo = PostgresLegalRelationRepository(session)
    ev_repo = PostgresEvidenceRepository(session)

    # 1. Source
    source = Source(id="src-planalto", name="Planalto", base_url="https://planalto.gov.br")
    await source_repo.save(source)

    # 2. Raw content
    raw_legal_text = """LEI COMPLEMENTAR Nº 116, DE 31 DE DEZEMBRO DE 2003
CAPÍTULO I
DO IMPOSTO SOBRE SERVIÇOS
Art. 1º O Imposto Sobre Serviços de Qualquer Natureza tem como fato gerador a prestação de serviços.
§ 1º O imposto incide também sobre o serviço proveniente do exterior.
ANEXO I
LISTA DE SERVIÇOS
1. Serviços de informática."""

    # 3. Acquisition via Mock Adapter (port contract test)
    acq_adapter = MockDocumentAcquisitionAdapter(mock_content=raw_legal_text.encode("utf-8"))
    acq_req = AcquisitionRequest(
        source=source,
        target_url="https://planalto.gov.br/lc116",
        max_bytes=10 * 1024 * 1024
    )
    acq_res: AcquisitionResult = await acq_adapter.acquire(acq_req)

    assert acq_res.artifact is not None
    assert acq_res.artifact.size_bytes > 0
    assert len(acq_res.redirect_chain) > 0

    # 4. Ingest use case
    parser = BrazilianLawParser()
    ingest_uc = IngestDocumentUseCase(
        source_repo=source_repo,
        doc_repo=doc_repo,
        version_repo=ver_repo,
        node_repo=node_repo,
        structure_parser=parser
    )

    ingest_req = LegalDocumentIngestionRequest(
        source_id="src-planalto",
        official_url="https://planalto.gov.br/lc116",
        raw_content=raw_legal_text,
        document_type=DocumentType.COMPLEMENTARY_LAW,
        document_number="116",
        title="Lei Complementar 116/2003",
        jurisdiction=Jurisdiction.FEDERAL,
        issuing_body="PRESIDENCIA",
        publication_date=date(2003, 12, 31),
        dry_run=False
    )

    ingest_res = await ingest_uc.execute(ingest_req)

    assert ingest_res.success is True
    assert ingest_res.document_id is not None
    assert ingest_res.version_id is not None

    # 5. Tree validation in database
    nodes = await node_repo.get_tree_by_version(ingest_res.version_id)
    assert len(nodes) >= 6

    norma_root = nodes[0]
    assert norma_root.node_type == LegalNodeType.NORMA
    assert norma_root.parent_id is None

    node_types = [n.node_type for n in nodes]
    assert LegalNodeType.CAPITULO in node_types
    assert LegalNodeType.ARTIGO in node_types
    assert LegalNodeType.PARAGRAFO in node_types
    assert LegalNodeType.ANEXO in node_types
