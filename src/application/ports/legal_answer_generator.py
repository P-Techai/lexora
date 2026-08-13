from abc import ABC, abstractmethod
from src.application.dto.context_pack import LegalContextPack
from src.domain.entities.legal_answer import LegalAnswer


class LegalAnswerGenerator(ABC):
    """Porta abstrata de aplicação para geração linguística controlada de respostas jurídicas a partir de um LegalContextPack."""

    @abstractmethod
    async def generate_answer(self, context_pack: LegalContextPack) -> LegalAnswer:
        """Gera uma resposta jurídica estruturada vinculada estritamente aos nós do contexto."""
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Nome identificador do provedor de geração."""
        pass

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Versão do modelo utilizado."""
        pass
