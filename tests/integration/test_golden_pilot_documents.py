from datetime import date
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.application.dto.ingestion_dto import LegalDocumentIngestionRequest
from src.application.parsers.brazilian_law_parser import BrazilianLawParser
from src.application.use_cases.legal.create_document import CreateDocumentUseCase
from src.application.use_cases.legal.ingest_document import IngestDocumentUseCase
from src.domain.entities.evidence import Evidence
from src.domain.entities.source import Source
from src.domain.enums import DocumentType, Jurisdiction, LegalNodeType
from src.infrastructure.adapters.html_txt_extractor import HtmlTxtDocumentExtractor
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

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def pilot_session():
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
async def test_golden_pilot_lc116_ingestion_and_parsing(pilot_session: AsyncSession):
    """
    TESTE GOLDEN DE INGESTÃO E DECOMPOSIÇÃO DO PILOTO LC 116/2003:
    Valida a ingestão controlada com extração de texto, parsing estrutural,
    criação da árvore determinística com raiz NORMA e zero perda silenciosa de dados.
    """
    source_repo = PostgresSourceRepository(pilot_session)
    doc_repo = PostgresLegalDocumentRepository(pilot_session)
    ver_repo = PostgresLegalVersionRepository(pilot_session)
    node_repo = PostgresLegalNodeRepository(pilot_session)
    rel_repo = PostgresLegalRelationRepository(pilot_session)
    ev_repo = PostgresEvidenceRepository(pilot_session)

    source = Source(id="src-planalto", name="Planalto Presidencia", base_url="https://planalto.gov.br")
    await source_repo.save(source)

    lc116_raw = """LEI COMPLEMENTAR Nº 116, DE 31 DE DEZEMBRO DE 2003
Art. 1º O Imposto Sobre Serviços de Qualquer Natureza tem como fato gerador a prestação de serviços.
§ 1º O imposto incide também sobre o serviço proveniente do exterior.
Art. 2º O imposto não incide sobre:
I - as exportações de serviços para o exterior;"""

    acq_adapter = MockDocumentAcquisitionAdapter(mock_content=lc116_raw.encode("utf-8"))
    parser = BrazilianLawParser()

    ingest_uc = IngestDocumentUseCase(
        doc_repo=doc_repo,
        version_repo=ver_repo,
        node_repo=node_repo,
        relation_repo=rel_repo,
        evidence_repo=ev_repo,
        source_repo=source_repo,
        acquisition_provider=acq_adapter,
        structure_parser=parser
    )

    req = LegalDocumentIngestionRequest(
        source_id="src-planalto",
        target_url="https://planalto.gov.br/lc116",
        document_type=DocumentType.COMPLEMENTARY_LAW,
        document_number="116",
        title="Lei Complementar 116/2003",
        jurisdiction=Jurisdiction.FEDERAL,
        issuing_body="PRESIDENCIA",
        publication_date=date(2003, 12, 31),
        dry_run=False
    )

    result = await ingest_uc.execute(req)

    assert result.success is True
    assert result.nodes_count >= 5
    assert result.version_id is not None

    # Valida estrutura da árvore persistida
    nodes = await node_repo.get_nodes_by_version(result.version_id)
    assert any(n.node_type == LegalNodeType.NORMA for n in nodes)
    assert any(n.identifier == "art-1" for n in nodes)
    assert any(n.identifier == "art-2" for n in nodes)
