from abc import ABC, abstractmethod
from typing import Any, Dict, List


class EmbeddingProvider(ABC):
    """Porta abstrata para geração de embeddings vetoriais."""

    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Gera o vetor de embedding para o texto fornecido."""
        pass


class RerankerProvider(ABC):
    """Porta abstrata para reordenamento semântico e hierárquico (Legal Reranker)."""

    @abstractmethod
    async def rerank(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """Reordena a lista de documentos com base na relevância semântica e jurídica."""
        pass


class QueueProvider(ABC):
    """Porta abstrata para envio de mensagens e tarefas assíncronas."""

    @abstractmethod
    async def publish(self, queue_name: str, payload: Dict[str, Any]) -> bool:
        """Publica uma mensagem em uma fila especificável."""
        pass


class SearchProvider(ABC):
    """Porta abstrata para motor de busca híbrido (Lexical BM25 + Vector)."""

    @abstractmethod
    async def search(self, query: str, filters: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
        """Executa busca híbrida combinada no repositório de documentos normativos."""
        pass
