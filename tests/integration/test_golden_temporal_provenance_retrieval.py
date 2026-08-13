from datetime import date
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.application.dto.ingestion_dto import LegalDocumentIngestionRequest
from src.application.dto.retrieval_dto import LegalRetrievalRequest
from src.application.parsers.brazilian_law_parser import BrazilianLawParser
from src.application.use_cases.legal.ingest_document import IngestDocumentUseCase
from src.application.use_cases.retrieval.retrieve_legal_evidence import HybridLegalRetrievalService
from src.domain.entities.source import Source
from src.domain.enums import DocumentType, Jurisdiction
from src.infrastructure.adapters.mock_acquisition import MockDocumentAcquisitionAdapter
from src.infrastructure.adapters.mock_embedding import MockEmbeddingProvider
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
async def retrieval_session():
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
async def test_golden_temporal_and_provenance_retrieval(retrieval_session: AsyncSession):
    """
    TESTE GOLDEN TEMPORAL E DE PROVENIÊNCIA (PROMPT 08):
    1. Ingere documento piloto (LC 116/2003).
    2. Executa busca híbrida com data de referência de vigência válida.
    3. Confirma que 100% dos resultados possuem a cadeia de proveniência de 5 níveis intacta.
    """
    session = retrieval_session

    source_repo = PostgresSourceRepository(session)
    doc_repo = PostgresLegalDocumentRepository(session)
    ver_repo = PostgresLegalVersionRepository(session)
    node_repo = PostgresLegalNodeRepository(session)
    rel_repo = PostgresLegalRelationRepository(session)
    ev_repo = PostgresEvidenceRepository(session)

    source = Source(id="src-planalto", name="Planalto", base_url="https://planalto.gov.br")
    await source_repo.save(source)

    raw_lc116 = """LEI COMPLEMENTAR Nº 116, DE 31 DE DEZEMBRO DE 2003
CAPÍTULO I
DO IMPOSTO SOBRE SERVIÇOS
Art. 1º O Imposto Sobre Serviços de Qualquer Natureza tem como fato gerador a prestação de serviços.
§ 1º O imposto incide também sobre o serviço proveniente do exterior."""

    acq_adapter = MockDocumentAcquisitionAdapter(mock_content=raw_lc116.encode("utf-8"))
    parser = BrazilianLawParser()

    ingest_uc = IngestDocumentUseCase(
        source_repo=source_repo,
        doc_repo=doc_repo,
        version_repo=ver_repo,
        node_repo=node_repo,
        relation_repo=rel_repo,
        evidence_repo=ev_repo,
        acquisition_provider=acq_adapter,
        structure_parser=parser
    )

    ingest_req = LegalDocumentIngestionRequest(
        source_id="src-planalto",
        official_url="https://planalto.gov.br/lc116",
        raw_content=raw_lc116,
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

    # Executa a busca híbrida com data de referência 2020-01-01
    mock_emb = MockEmbeddingProvider()
    retrieval_service = HybridLegalRetrievalService(
        node_repo=node_repo,
        version_repo=ver_repo,
        doc_repo=doc_repo,
        source_repo=source_repo,
        evidence_repo=ev_repo,
        embedding_provider=mock_emb
    )

    ret_req = LegalRetrievalRequest(
        query="fato gerador prestacao de servicos Art. 1º",
        reference_date=date(2020, 1, 1),
        jurisdiction=Jurisdiction.FEDERAL,
        document_number="116",
        top_k=5
    )

    ret_res = await retrieval_service.execute(ret_req)

    assert ret_res.provenance_valid is True
    assert len(ret_res.results) > 0

    top_item = ret_res.results[0]
    assert top_item.identifier == "art-1"
    assert top_item.provenance_chain.get("source_id") == "src-planalto"
    assert top_item.provenance_chain.get("legal_document_id") == ingest_res.document_id
    assert top_item.provenance_chain.get("legal_version_id") == ingest_res.version_id
    assert top_item.provenance_chain.get("legal_node_id") == top_item.legal_node_id
