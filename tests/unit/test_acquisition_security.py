import pytest

from src.application.dto.acquisition_dto import AcquisitionRequest
from src.application.services.source_registry import SourceRegistryService
from src.domain.entities.source import Source
from src.domain.exceptions import ArtifactTooLargeError, SSRFProtectionError
from src.infrastructure.adapters.http_acquisition import HttpDocumentAcquisitionAdapter


@pytest.mark.asyncio
async def test_acquisition_security_ssrf_blocking():
    source = Source(id="src-planalto", name="Planalto", base_url="https://planalto.gov.br")
    registry = SourceRegistryService()
    registry.register_source(source, allowed_domains=["planalto.gov.br"])

    adapter = HttpDocumentAcquisitionAdapter(source_registry=registry)

    # Tenta acessar IP de metadata interno (SSRF)
    req = AcquisitionRequest(
        source=source,
        target_url="http://169.254.169.254/latest/meta-data/"
    )

    with pytest.raises(SSRFProtectionError):
        await adapter.acquire(req)


@pytest.mark.asyncio
async def test_acquisition_security_subdomain_bypass_blocking():
    source = Source(id="src-planalto", name="Planalto", base_url="https://planalto.gov.br")
    registry = SourceRegistryService()
    registry.register_source(source, allowed_domains=["planalto.gov.br"])

    adapter = HttpDocumentAcquisitionAdapter(source_registry=registry)

    # Tenta ataque de bypass por sufixo de domínio (evilplanalto.gov.br ou planalto.gov.br.attacker.com)
    req = AcquisitionRequest(
        source=source,
        target_url="https://planalto.gov.br.attacker.com/fake-lei"
    )

    with pytest.raises(SSRFProtectionError):
        await adapter.acquire(req)
