from datetime import date, datetime
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.infrastructure.db.base import Base
from src.infrastructure.db.repositories.postgres_repositories import (
    PostgresEvidenceRepository,
    PostgresLegalDocumentRepository,
    PostgresLegalNodeRepository,
    PostgresLegalRelationRepository,
    PostgresLegalVersionRepository,
    PostgresSourceRepository,
)
from src.domain.entities.source import Source
from src.domain.entities.legal_document import LegalDocument
from src.domain.entities.legal_version import LegalVersion
from src.domain.entities.legal_node import LegalNode
from src.domain.entities.legal_relation import LegalRelation
from src.domain.entities.evidence import Evidence
from src.domain.enums import (
    DocumentType,
    Jurisdiction,
    LegalNodeType,
    LegalRelationType,
    VersionStatus,
)

# Test Engine usando SQLite assíncrono em memória para execução rápida sem dependências externas
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
async def test_full_repository_lifecycle(test_session: AsyncSession):
    source_repo = PostgresSourceRepository(test_session)
    doc_repo = PostgresLegalDocumentRepository(test_session)
    version_repo = PostgresLegalVersionRepository(test_session)
    node_repo = PostgresLegalNodeRepository(test_session)
    relation_repo = PostgresLegalRelationRepository(test_session)
    evidence_repo = PostgresEvidenceRepository(test_session)

    # 1. Inserir Source
    source = Source(
        id="src-planalto-001",
        name="Portal do Planalto",
        official=True,
        authority_level=1,
        base_url="https://www.planalto.gov.br",
        jurisdiction=Jurisdiction.FEDERAL,
        active=True
    )
    saved_source = await source_repo.save(source)
    assert saved_source.id == "src-planalto-001"

    # 2. Inserir LegalDocument
    doc = LegalDocument(
        id="doc-lei-8112",
        source_id=saved_source.id,
        document_type=DocumentType.ORDINARY_LAW,
        document_number="8112",
        title="Lei nº 8.112, de 11 de dezembro de 1990",
        ementa="Dispõe sobre o regime jurídico dos servidores públicos civis da União...",
        jurisdiction=Jurisdiction.FEDERAL,
        issuing_body="PRESIDENCIA_DA_REPUBLICA",
        publication_date=date(1990, 12, 12),
        document_hash="hash-doc-8112"
    )
    saved_doc = await doc_repo.save(doc)
    assert saved_doc.document_number == "8112"

    # 3. Inserir LegalVersion
    ver = LegalVersion(
        id="ver-8112-v1",
        legal_document_id=saved_doc.id,
        version_number=1,
        content_hash="hash-ver-v1",
        effective_from=date(1990, 12, 12),
        effective_until=None,
        status=VersionStatus.ACTIVE
    )
    saved_ver = await version_repo.save(ver)
    assert saved_ver.id == "ver-8112-v1"

    # 4. Inserir LegalNodes (Árvore Hierárquica)
    art_1 = LegalNode(
        id="node-art-1",
        legal_version_id=saved_ver.id,
        parent_id=None,
        node_type=LegalNodeType.ARTIGO,
        identifier="art-1",
        label="Art. 1º",
        text="Esta Lei institui o Regime Jurídico dos Servidores Públicos Civis...",
        path="/art-1",
        position=1,
        content_hash="hash-art-1",
        effective_from=date(1990, 12, 12)
    )
    par_1 = LegalNode(
        id="node-par-1",
        legal_version_id=saved_ver.id,
        parent_id="node-art-1",
        node_type=LegalNodeType.PARAGRAFO,
        identifier="par-1",
        label="Parágrafo único",
        text="Para os efeitos desta Lei, servidor é a pessoa legalmente investida em cargo público.",
        path="/art-1/par-1",
        position=1,
        content_hash="hash-par-1",
        effective_from=date(1990, 12, 12)
    )
    await node_repo.save(art_1)
    await node_repo.save(par_1)

    children = await node_repo.get_children("node-art-1")
    assert len(children) == 1
    assert children[0].id == "node-par-1"

    # 5. Inserir Evidence e LegalRelation
    ev = Evidence(
        id="ev-001",
        source_id=saved_source.id,
        legal_document_id=saved_doc.id,
        legal_version_id=saved_ver.id,
        legal_node_id=art_1.id,
        quote_or_excerpt="Excerto do Diário Oficial da União",
        content_hash="hash-ev-001",
        captured_at=datetime.utcnow()
    )
    saved_ev = await evidence_repo.save(ev)
    assert saved_ev.id == "ev-001"

    rel = LegalRelation(
        id="rel-001",
        source_node_id=par_1.id,
        target_node_id=art_1.id,
        relation_type=LegalRelationType.REGULATES,
        confidence=1.0,
        evidence_id=saved_ev.id
    )
    saved_rel = await relation_repo.save(rel)
    assert saved_rel.relation_type == LegalRelationType.REGULATES

    # 6. Testar Consulta Temporal da Versão
    effective_ver = await version_repo.get_effective_version(saved_doc.id, date(2026, 8, 11))
    assert effective_ver is not None
    assert effective_ver.id == "ver-8112-v1"
