from datetime import datetime
from typing import Dict, Optional

from src.application.dto.acquisition_dto import AcquisitionRequest, AcquisitionResult
from src.application.ports.acquisition_provider import DocumentAcquisitionProvider
from src.domain.exceptions import ArtifactTooLargeError, UnsupportedContentTypeError
from src.domain.services.hash_service import DocumentHashCalculator


class MockDocumentAcquisitionAdapter(DocumentAcquisitionProvider):
    """Adaptador mock para simulação de captura de artefatos brutos em testes unitários e de integração."""

    def __init__(self, synthetic_content: Optional[bytes] = None, content_type: str = "text/plain"):
        self.synthetic_content = synthetic_content or b"Art. 1º Conteudo sintetico de teste do Lexora."
        self.content_type = content_type

    async def acquire(self, request: AcquisitionRequest) -> AcquisitionResult:
        size = len(self.synthetic_content)
        if size > request.max_size_bytes:
            raise ArtifactTooLargeError(f"Artefato possui {size} bytes, excedendo o limite de {request.max_size_bytes} bytes.")

        if self.content_type not in request.allowed_content_types:
            raise UnsupportedContentTypeError(f"MIME type '{self.content_type}' não é suportado pelo contrato.")

        content_hash = DocumentHashCalculator.calculate_sha256(self.synthetic_content)

        return AcquisitionResult(
            source_id=request.source_id,
            url=request.url,
            status_code=200,
            content_type=self.content_type,
            size_bytes=size,
            raw_bytes=self.synthetic_content,
            content_hash=content_hash,
            captured_at=datetime.utcnow(),
            redirect_chain=[request.url],
            headers={"Server": "MockServer/1.0"}
        )
