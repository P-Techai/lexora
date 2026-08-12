import pytest

from src.application.dto.acquisition_dto import AcquisitionRequest
from src.domain.exceptions import ArtifactTooLargeError, UnsupportedContentTypeError
from src.infrastructure.adapters.mock_acquisition import MockDocumentAcquisitionAdapter


@pytest.mark.asyncio
async def test_mock_acquisition_size_limit():
    adapter = MockDocumentAcquisitionAdapter(synthetic_content=b"X" * 1000)
    req = AcquisitionRequest(
        source_id="src-test",
        url="https://planalto.gov.br/lei",
        max_size_bytes=500  # Limite menor que 1000 bytes
    )

    with pytest.raises(ArtifactTooLargeError):
        await adapter.acquire(req)


@pytest.mark.asyncio
async def test_mock_acquisition_content_type_validation():
    adapter = MockDocumentAcquisitionAdapter(synthetic_content=b"Content", content_type="video/mp4")
    req = AcquisitionRequest(
        source_id="src-test",
        url="https://planalto.gov.br/lei",
        allowed_content_types=["text/plain", "application/pdf"]
    )

    with pytest.raises(UnsupportedContentTypeError):
        await adapter.acquire(req)
