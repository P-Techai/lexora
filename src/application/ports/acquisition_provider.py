from abc import ABC, abstractmethod

from src.application.dto.acquisition_dto import AcquisitionRequest, AcquisitionResult


class DocumentAcquisitionProvider(ABC):
    """Porta de abstração para captura e aquisição segura de documentos brutos de fontes externas."""

    @abstractmethod
    async def acquire(self, request: AcquisitionRequest) -> AcquisitionResult:
        """Executa a aquisição controlada do artefato bruto retornando o AcquisitionResult."""
        pass
