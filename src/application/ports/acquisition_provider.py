from abc import ABC, abstractmethod
from src.application.dto.acquisition_dto import AcquisitionRequest, AcquisitionResult


class DocumentAcquisitionProvider(ABC):
    """Porta abstrata unificada para provedores de aquisição de documentos de fontes oficiais."""

    @abstractmethod
    async def acquire(self, request: AcquisitionRequest) -> AcquisitionResult:
        """Adquire um artefato normativo bruto da fonte oficial especificada no AcquisitionRequest."""
        pass
