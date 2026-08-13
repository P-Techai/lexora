from abc import ABC, abstractmethod
from pydantic import BaseModel
from src.domain.entities.raw_artifact import RawArtifact


class ExtractedDocumentText(BaseModel):
    """Resultado da extração de texto bruto de um artefato."""
    raw_text: str
    content_type: str
    encoding: str = "utf-8"
    extracted_metadata: dict = {}


class DocumentExtractor(ABC):
    """Porta abstrata para extração de texto bruto a partir de RawArtifacts."""

    @abstractmethod
    def extract_text(self, artifact: RawArtifact, content_bytes: bytes) -> ExtractedDocumentText:
        """Extrai o texto bruto contido no artefato decodificando HTML, TXT ou PDF."""
        pass
