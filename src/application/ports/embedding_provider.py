from abc import ABC, abstractmethod
from typing import List


class EmbeddingProvider(ABC):
    """Porta abstrata para provedores de modelos de Embedding vetorial. Domínio puro (0 dependências de SDKs)."""

    @abstractmethod
    async def get_embedding(self, text: str) -> List[float]:
        """Gera um vetor de embedding para uma string de texto."""
        pass

    @abstractmethod
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Gera vetores de embedding em lote (batch) para uma lista de textos."""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Nome identificador do modelo de embedding."""
        pass

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Versão do modelo de embedding."""
        pass

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Número de dimensões do vetor gerado pelo modelo."""
        pass
