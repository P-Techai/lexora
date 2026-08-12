from datetime import date
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.application.dto.temporal_dto import TemporalQueryRequest
from src.application.use_cases/legal.create_document import CreateDocumentUseCase
from src.application.use_cases/legal.create_version import CreateVersionUseCase
from src.application.use_cases/legal.query_legal_at_date import QueryLegalAtDateUseCase
from src.application.use_cases/legal.revoke_legal_document import RevokeLegalDocumentUseCase
from src.application.use_cases/legal.revoke_legal_node import RevokeLegalNodeUseCase
from src.domain.entities.evidence import Evidence
from src.domain.entities.legal_node import LegalNode
from src.domain.entities.source import Source
from src.domain.enums import DocumentType, Jurisdiction, LegalNodeType, TemporalStatus
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
async def test_golden_historical_scenario_full_document_revocation(test_session: AsyncSession):
    """
    CENÁRIO GOLDEN DE REVOGAÇÃO TOTAL:
    Documento A criado com V1 (2020 a 2022) e V2 (2022 em diante).
    Em 2024, o Documento B revoga o Documento A com efeito a partir de 2024-01-01.
    Verifica que consultas prévias (2021 e 2023) continuam retornando EFFECTIVE, e após 2024 retornam REVOKED.
    """
    source_repo = PostgresSourceRepository(test_session)
    doc_repo = PostgresLegalDocumentRepository(test_session)
    ver_repo = PostgresLegalVersionRepository(test_session)
    node_repo = PostgresLegalNodeRepository(test_session)
    rel_repo = PostgresLegalRelationRepository(test_session)
    ev_repo = PostgresEvidenceRepository(test_session)

    await source_repo.save(Source(id="src-planalto", name="Planalto"))

    evidence = Evidence(
        id="ev-dou-revogacao-2024",
        source_id="src-planalto",
        content_excerpt="Lei B revoga a Lei A expressamente.",
        official_url="https://dou.gov.br/lei-b",
        captured_at=date(2024, 1, 1)
    )
    await ev_repo.save(evidence)

    # 1. Criar Documento A
    create_doc = CreateDocumentUseCase(doc_repo, source_repo)
    doc_a, _ = await create_doc.execute(
        source_id="src-planalto",
        document_type=DocumentType.ORDINARY_LAW,
        document_number="1000",
        title="Lei A (Original 2020)",
        ementa="Ementa da Lei A",
        jurisdiction=Jurisdiction.FEDERAL,
        issuing_body="PRESIDENCIA",
        publication_date=date(2020, 1, 1),
        official_url="https://planalto.gov.br/l1000",
        document_hash="hash-lei-a-v1"
    )

    create_ver = CreateVersionUseCase(ver_repo, doc_repo)
    # Versão 1: [2020-01-01, 2022-01-01)
    ver1, _ = await create_ver.execute(
        legal_document_id=doc_a.id,
        content_hash="hash-lei-a-v1",
        published_at=date(2020, 1, 1),
        effective_from=date(2020, 1, 1),
        effective_until=date(2022, 1, 1)
    )

    # Versão 2: [2022-01-01, NULL) - Vigência aberta original
    ver2, _ = await create_ver.execute(
        legal_document_id=doc_a.id,
        content_hash="hash-lei-a-v2",
        published_at=date(2022, 1, 1),
        effective_from=date(2022, 1, 1)
    )

    node_v1 = LegalNode(
        id="node-v1-art1",
        legal_version_id=ver1.id,
        node_type=LegalNodeType.ARTIGO,
        identifier="art-1",
        label="Art. 1º",
        text="Art. 1º Redação 2020",
        path="/art-1",
        position=1,
        content_hash="hv1"
    )
    await node_repo.save(node_v1)

    node_v2 = LegalNode(
        id="node-v2-art1",
        legal_version_id=ver2.id,
        node_type=LegalNodeType.ARTIGO,
        identifier="art-1",
        label="Art. 1º",
        text="Art. 1º Redação 2022 alterada",
        path="/art-1",
        position=1,
        content_hash="hv2"
    )
    await node_repo.save(node_v2)

    query_uc = QueryLegalAtDateUseCase(doc_repo, ver_repo, node_repo, rel_repo, ev_repo)

    # 2. Consultas ANTES da revogação
    res_2021 = await query_uc.execute(TemporalQueryRequest(document_id=doc_a.id, target_date=date(2021, 6, 1)))
    assert res_2021.status == TemporalStatus.EFFECTIVE
    assert res_2021.version_id == ver1.id

    res_2023 = await query_uc.execute(TemporalQueryRequest(document_id=doc_a.id, target_date=date(2023, 6, 1)))
    assert res_2023.status == TemporalStatus.EFFECTIVE
    assert res_2023.version_id == ver2.id

    # 3. Executar o Evento de Revogação em 2024-01-01
    revoke_uc = RevokeLegalDocumentUseCase(doc_repo, ver_repo, node_repo, rel_repo, ev_repo)
    await revoke_uc.execute(
        document_id=doc_a.id,
        revocation_date=date(2024, 1, 1),
        evidence_id="ev-dou-revogacao-2024"
    )

    # 4. Consultas APÓS a revogação (em 2025)
    res_2025 = await query_uc.execute(TemporalQueryRequest(document_id=doc_a.id, target_date=date(2025, 1, 1)))
    assert res_2025.status == TemporalStatus.REVOKED
    assert any("revogada" in w for w in res_2025.warnings)

    # 5. TESTE DE IMUTABILIDADE HISTÓRICA REPETIDO: Consultar 2021 e 2023 DEPOIS da revogação registrada!
    res_2021_again = await query_uc.execute(TemporalQueryRequest(document_id=doc_a.id, target_date=date(2021, 6, 1)))
    assert res_2021_again.status == TemporalStatus.EFFECTIVE, "A consulta histórica em 2021 deveria continuar EFFECTIVE!"

    res_2023_again = await query_uc.execute(TemporalQueryRequest(document_id=doc_a.id, target_date=date(2023, 6, 1)))
    assert res_2023_again.status == TemporalStatus.EFFECTIVE, "A consulta histórica em 2023 deveria continuar EFFECTIVE!"


@pytest.mark.asyncio
async def test_golden_historical_scenario_partial_revocation(test_session: AsyncSession):
    """
    CENÁRIO GOLDEN DE REVOGAÇÃO PARCIAL:
    Documento possui Art. 1º, Art. 2º e Art. 3º.
    O Art. 2º é revogado em 2024.
    Consultas em 2023 mostram todos os 3 artigos ativos.
    Consultas em 2025 mostram apenas Art. 1º e Art. 3º ativos, e o Art. 2º revogado.
    """
    source_repo = PostgresSourceRepository(test_session)
    doc_repo = PostgresLegalDocumentRepository(test_session)
    ver_repo = PostgresLegalVersionRepository(test_session)
    node_repo = PostgresLegalNodeRepository(test_session)
    rel_repo = PostgresLegalRelationRepository(test_session)
    ev_repo = PostgresEvidenceRepository(test_session)

    await source_repo.save(Source(id="src-planalto", name="Planalto"))
    await ev_repo.save(Evidence(id="ev-parcial-2024", source_id="src-planalto", captured_at=date(2024, 1, 1)))

    create_doc = CreateDocumentUseCase(doc_repo, source_repo)
    doc, _ = await create_doc.execute(
        source_id="src-planalto",
        document_type=DocumentType.ORDINARY_LAW,
        document_number="2000",
        title="Lei com 3 Artigos",
        jurisdiction=Jurisdiction.FEDERAL,
        issuing_body="PRESIDENCIA",
        publication_date=date(2020, 1, 1),
        document_hash="h2000"
    )

    create_ver = CreateVersionUseCase(ver_repo, doc_repo)
    ver, _ = await create_ver.execute(
        legal_document_id=doc.id,
        content_hash="h2000",
        effective_from=date(2020, 1, 1)
    )

    art1 = LegalNode(id="n-art1", legal_version_id=ver.id, node_type=LegalNodeType.ARTIGO, identifier="art-1", label="Art. 1º", text="Art. 1", path="/art-1", position=1, content_hash="h-a1")
    art2 = LegalNode(id="n-art2", legal_version_id=ver.id, node_type=LegalNodeType.ARTIGO, identifier="art-2", label="Art. 2º", text="Art. 2", path="/art-2", position=2, content_hash="h-a2")
    art3 = LegalNode(id="n-art3", legal_version_id=ver.id, node_type=LegalNodeType.ARTIGO, identifier="art-3", label="Art. 3º", text="Art. 3", path="/art-3", position=3, content_hash="h-a3")

    await node_repo.save_bulk([art1, art2, art3])

    query_uc = QueryLegalAtDateUseCase(doc_repo, ver_repo, node_repo, rel_repo, ev_repo)

    # Consulta 2023 -> Todos os 3 artigos presentes
    res_2023 = await query_uc.execute(TemporalQueryRequest(document_id=doc.id, target_date=date(2023, 1, 1)))
    assert len(res_2023.nodes) == 3

    # Executar Revogação Parcial apenas do Artigo 2 em 2024
    revoke_node_uc = RevokeLegalNodeUseCase(node_repo, rel_repo, ev_repo)
    await revoke_node_uc.execute(
        node_id=art2.id,
        revocation_date=date(2024, 1, 1),
        evidence_id="ev-parcial-2024",
        revoking_node_id=art1.id
    )

    # Consulta 2025 -> Apens Art. 1 e Art. 3 ativos
    res_2025 = await query_uc.execute(TemporalQueryRequest(document_id=doc.id, target_date=date(2025, 1, 1)))
    active_identifiers = [n.identifier for n in res_2025.nodes]
    assert "art-1" in active_identifiers
    assert "art-3" in active_identifiers
    assert "art-2" not in active_identifiers, "O Artigo 2º revogado não deve estar na árvore ativa em 2025!"
