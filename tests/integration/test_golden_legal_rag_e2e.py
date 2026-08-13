from datetime import date
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.application.dto.ingestion_dto import LegalDocumentIngestionRequest
from src.application.parsers.brazilian_law_parser import BrazilianLawParser
from src.application.use_cases.legal.ingest_document import IngestDocumentUseCase
from src.domain.entities.source import Source
from src.domain.enums import DocumentType, Jurisdiction, LegalAnswerStatus
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
from src.interfaces.api/main import app

SQLITE_MEMORY_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def e2e_rag_session():
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
async def test_golden_legal_rag_end_to_end_pipeline(e2e_rag_session: AsyncSession):
    """
    TESTE GOLDEN END-TO-END DE RAG JURÍDICO CONTEXTUAL (PROMPT 09 § 21):
    Pipeline Completo:
    QUERY -> RETRIEVAL -> CONTEXT PACK -> LLM GENERATION -> GUARDRAILS VALIDATION -> CITATION VALIDATION -> FINAL RESPONSE.
    """
    session = e2e_rag_session

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

    # Dependency override para o teste HTTP FastAPI
    async def _get_test_session():
        yield session

    app.dependency_overrides[get_db_session] = _get_test_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Caso Suportado: Consulta válida na data de referência
        payload = {
            "query": "Qual o fato gerador do ISS Art. 1º",
            "reference_date": "2020-01-01",
            "jurisdiction": "FEDERAL",
            "document_type": "COMPLEMENTARY_LAW",
            "document_number": "116",
            "top_k": 5
        }
        res = await client.post("/api/v1/legal/answer", json=payload)
        assert res.status_code == 200

        data = res.json()
        assert data["status"] == LegalAnswerStatus.SUPPORTED
        assert data["abstained"] is False
        assert len(data["citations"]) > 0
        assert data["citations"][0]["identifier"] == "art-1"
        assert data["citations"][0]["raw_artifact_hash"] is not None

        # 2. Caso de Abstenção: Consulta sem evidência normativa cadastrada
        payload_missing = {
            "query": "Cálculo de imposto de exportação de foguetes espaciais",
            "reference_date": "2020-01-01",
            "jurisdiction": "MUNICIPAL",
            "document_number": "99999",
            "top_k": 5
        }
        res_missing = await client.post("/api/v1/legal/answer", json=payload_missing)
        assert res_missing.status_code == 200

        data_missing = res_missing.json()
        assert data_missing["abstained"] is True
        assert data_missing["status"] in (LegalAnswerStatus.INSUFFICIENT_EVIDENCE, LegalAnswerStatus.CONFLICTING_SOURCES)

    app.dependency_overrides.clear()
