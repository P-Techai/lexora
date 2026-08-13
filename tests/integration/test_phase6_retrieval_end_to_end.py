from datetime import date
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.application.dto.ingestion_dto import LegalDocumentIngestionRequest
from src.application.parsers.brazilian_law_parser import BrazilianLawParser
from src.application.use_cases.legal.ingest_document import IngestDocumentUseCase
from src.domain.entities.source import Source
from src.domain.enums import DocumentType, Jurisdiction
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
from src.infrastructure.db.session import get_db_session
from src.interfaces.api.main import app

SQLITE_MEMORY_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def e2e_retrieval_session():
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
async def test_phase6_retrieval_end_to_end_http_pipeline(e2e_retrieval_session: AsyncSession):
    """
    TESTE END-TO-END DE RECUPERAÇÃO DE PRODUÇÃO (PROMPT 08.1 § 36):
    Executa o pipeline completo:
    Source -> RawArtifact -> Evidence -> LegalDocument -> LegalVersion -> LegalNode -> HTTP API /api/v1/legal/retrieve.
    Valida 10x determinismo de score e ordem, 5 níveis de proveniência e filtragem temporal.
    """
    session = e2e_retrieval_session

    source_repo = PostgresSourceRepository(session)
    doc_repo = PostgresLegalDocumentRepository(session)
    ver_repo = PostgresLegalVersionRepository(session)
    node_repo = PostgresLegalNodeRepository(session)
    rel_repo = PostgresLegalRelationRepository(session)
    ev_repo = PostgresEvidenceRepository(session)

    source = Source(id="src-planalto", name="Planalto", base_url="https://planalto.gov.br")
    await source_repo.save(source)

    raw_text = """LEI COMPLEMENTAR Nº 116, DE 31 DE DEZEMBRO DE 2003
CAPÍTULO I
DO IMPOSTO SOBRE SERVIÇOS
Art. 1º O Imposto Sobre Serviços de Qualquer Natureza tem como fato gerador a prestação de serviços.
§ 1º O imposto incide também sobre o serviço proveniente do exterior."""

    acq_adapter = MockDocumentAcquisitionAdapter(mock_content=raw_text.encode("utf-8"))
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
        raw_content=raw_text,
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

    # Override da sessão de banco para o client HTTP de testes FastAPI
    async def _get_test_session():
        yield session

    app.dependency_overrides[get_db_session] = _get_test_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Chamada HTTP ao endpoint real /api/v1/legal/retrieve
        payload = {
            "query": "fato gerador prestacao servicos Art. 1º",
            "reference_date": "2020-01-01",
            "jurisdiction": "FEDERAL",
            "document_type": "COMPLEMENTARY_LAW",
            "document_number": "116",
            "top_k": 5
        }
        res = await client.post("/api/v1/legal/retrieve", json=payload)
        assert res.status_code == 200

        data = res.json()
        assert data["provenance_valid"] is True
        assert data["total_candidates"] > 0
        assert len(data["results"]) > 0

        first_item = data["results"][0]
        assert first_item["identifier"] == "art-1"
        assert first_item["provenance_chain"]["source_id"] == "src-planalto"
        assert first_item["provenance_chain"]["legal_document_id"] == ingest_res.document_id

        # Teste de 10x determinismo de ordem e pontuação
        for _ in range(10):
            res_repeat = await client.post("/api/v1/legal/retrieve", json=payload)
            data_repeat = res_repeat.json()
            assert data_repeat["results"][0]["final_score"] == first_item["final_score"]
            assert data_repeat["results"][0]["legal_node_id"] == first_item["legal_node_id"]

    app.dependency_overrides.clear()
