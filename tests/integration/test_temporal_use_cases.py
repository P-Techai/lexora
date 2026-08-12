from datetime import date
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.application.dto.temporal_dto import TemporalQueryRequest
from src.application.use_cases.legal.create_document import CreateDocumentUseCase
from src.application.use_cases.legal.create_version import CreateVersionUseCase
from src.application.use_cases.legal.query_legal_at_date import QueryLegalAtDateUseCase
from src.application.use_cases.legal.revoke_legal_document import RevokeLegalDocumentUseCase
from src.application.use_cases.legal.revoke_legal_node import RevokeLegalNodeUseCase
from src.domain.entities.evidence import Evidence
from src.domain.entities.legal_node import LegalNode
from src.domain.entities.source import Source
from src.domain.enums import DocumentType, Jurisdiction, LegalNodeType, LegalRelationType, TemporalStatus
from src.domain.exceptions import MissingEvidenceError
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
async def test_query_legal_at_date_and_total_revocation(test_session: AsyncSession):
    source_repo = PostgresSourceRepository(test_session)
    doc_repo = PostgresLegalDocumentRepository(test_session)
    ver_repo = PostgresLegalVersionRepository(test_session)
    node_repo = PostgresLegalNodeRepository(test_session)
    rel_repo = PostgresLegalRelationRepository(test_session)
    ev_repo = PostgresEvidenceRepository(test_session)

    # 1. Setup Source, Evidência e Documento
    await source_repo.save(Source(id="src-planalto", name="Planalto"))
    
    evidence = Evidence(
        id="ev-dou-123",
        source_id="src-planalto",
        content_excerpt="Publicação oficial de revogação no DOU",
        official_url="https://dou.gov.br/revogacao",
        captured_at=date(2025, 1, 1)
    )
    await ev_repo.save(evidence)

    create_doc_uc = CreateDocumentUseCase(doc_repo, source_repo)
    doc, _ = await create_doc_uc.execute(
        source_id="src-planalto",
        document_type=DocumentType.ORDINARY_LAW,
        document_number="7777",
        title="Lei 7777",
        ementa="Ementa da lei 7777",
        jurisdiction=Jurisdiction.FEDERAL,
        issuing_body="PRESIDENCIA",
        publication_date=date(2020, 1, 1),
        official_url="https://planalto.gov.br/l7777",
        document_hash="hash7777"
    )

    create_ver_uc = CreateVersionUseCase(ver_repo, doc_repo)
    version, _ = await create_ver_uc.execute(
        legal_document_id=doc.id,
        content_hash="hash7777",
        published_at=date(2020, 1, 1),
        effective_from=date(2020, 1, 1)
    )

    # Salvar nó da árvore
    node_art1 = LegalNode(
        id="node-art1",
        legal_version_id=version.id,
        node_type=LegalNodeType.ARTIGO,
        identifier="art-1",
        label="Art. 1º",
        text="Art. 1º Texto original",
        path="/art-1",
        position=1,
        content_hash="h-art1"
    )
    await node_repo.save(node_art1)

    query_uc = QueryLegalAtDateUseCase(doc_repo, ver_repo, node_repo, rel_repo, ev_repo)

    # 2. Consulta em 2022 -> STATUS EFFECTIVE
    res_2022 = await query_uc.execute(TemporalQueryRequest(document_id=doc.id, target_date=date(2022, 6, 1)))
    assert res_2022.status == TemporalStatus.EFFECTIVE
    assert res_2022.version_id == version.id
    assert len(res_2022.nodes) == 1

    # 3. Tentativa de Revogação Sem Evidência Válida -> Lança MissingEvidenceError
    revoke_uc = RevokeLegalDocumentUseCase(doc_repo, ver_repo, node_repo, rel_repo, ev_repo)
    with pytest.raises(MissingEvidenceError):
        await revoke_uc.execute(
            document_id=doc.id,
            revocation_date=date(2025, 1, 1),
            evidence_id="ev-inexistente"
        )

    # 4. Revogação Total Com Evidência Válida em 2025-01-01
    revoked = await revoke_uc.execute(
        document_id=doc.id,
        revocation_date=date(2025, 1, 1),
        evidence_id="ev-dou-123"
    )
    assert revoked is True

    # 5. Consulta após a revogação (em 2026) -> STATUS REVOKED
    res_2026 = await query_uc.execute(TemporalQueryRequest(document_id=doc.id, target_date=date(2026, 1, 1)))
    assert res_2026.status == TemporalStatus.REVOKED

    # 6. CONFIRMAÇÃO DE IMUTABILIDADE: O registro do documento e da versão PERMANECEM NO BANCO (0 SQL DELETES)
    assert await doc_repo.get_by_id(doc.id) is not None
    assert await ver_repo.get_by_id(version.id) is not None
