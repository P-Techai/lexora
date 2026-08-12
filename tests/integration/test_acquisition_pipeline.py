import os
import shutil
import tempfile
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.application.dto.acquisition_dto import AcquisitionRequest
from src.application.services.source_registry import SourceRegistryService
from src.application.use_cases/legal.acquire_artifact import AcquireArtifactUseCase
from src.domain.entities.source import Source
from src.domain.enums import SourcePolicy
from src.infrastructure.adapters.local_storage import LocalStorageAdapter
from src.infrastructure.adapters.mock_acquisition import MockDocumentAcquisitionAdapter
from src.infrastructure.db.base import Base
from src.infrastructure.db.repositories.postgres_repositories import PostgresSourceRepository

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
async def test_acquire_artifact_pipeline_integration(test_session: AsyncSession):
    temp_dir = tempfile.mkdtemp()
    try:
        source_repo = PostgresSourceRepository(test_session)

        # Inserir Source no repositório
        source = Source(id="src-planalto", name="Planalto", authority_level=1)
        await source_repo.save(source)

        # Configurar Registro de Fontes e Allowlist
        registry = SourceRegistryService(source_repo)
        registry.register_source_policy(
            source_id="src-planalto",
            policy=SourcePolicy.PRIMARY_OFFICIAL,
            allowed_domains=["planalto.gov.br"]
        )

        storage_adapter = LocalStorageAdapter(base_path=temp_dir)
        acq_adapter = MockDocumentAcquisitionAdapter(synthetic_content=b"Art. 1º Conteudo bruto da lei.")

        use_case = AcquireArtifactUseCase(
            acquisition_provider=acq_adapter,
            source_registry=registry,
            storage_provider=storage_adapter
        )

        req = AcquisitionRequest(
            source_id="src-planalto",
            url="https://www.planalto.gov.br/ccivil_03/leis/l8112.htm"
        )

        artifact, audit = await use_case.execute(req)

        assert artifact.source_id == "src-planalto"
        assert artifact.url == req.url
        assert len(artifact.content_hash) == 64
        assert audit.success is True
        assert audit.status_code == 200

        # Verificar gravação real no Storage local
        assert await storage_adapter.exists(artifact.storage_key) is True
        stored_bytes = await storage_adapter.get_bytes(artifact.storage_key)
        assert stored_bytes == b"Art. 1º Conteudo bruto da lei."

    finally:
        shutil.rmtree(temp_dir)
