import hashlib
import math
from typing import List

from src.application.ports.embedding_provider import EmbeddingProvider


class MockEmbeddingProvider(EmbeddingProvider):
    """Adaptador mock determinístico para geração de vetores de embedding em ambientes de testes e desenvolvimento."""

    def __init__(self, model_name: str = "text-embedding-3-small", model_version: str = "1.0.0", dimensions: int = 1536):
        self._model_name = model_name
        self._model_version = model_version
        self._dimensions = dimensions

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def model_version(self) -> str:
        return self._model_version

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def _generate_vector(self, text: str) -> List[float]:
        """Gera um vetor de boias de tamanho fixo normalizado com base no hash SHA-256 do texto de entrada."""
        raw_hash = hashlib.sha256(text.encode("utf-8")).digest()
        vector = []
        for i in range(self._dimensions):
            byte_val = raw_hash[i % len(raw_hash)]
            val = (byte_val / 255.0) * 2.0 - 1.0
            vector.append(val)

        # Normalização de magnitude (L2 norm)
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector

    async def get_embedding(self, text: str) -> List[float]:
        return self._generate_vector(text)

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        return [self._generate_vector(text) for text in texts]
