import os
from typing import Optional

from src.application.ports.embedding_provider import EmbeddingProvider
from src.domain.exceptions import ConfigurationError
from src.infrastructure.adapters.mock_embedding import MockEmbeddingProvider


class EmbeddingProviderFactory:
    """Factory para instanciação de provedores de embedding baseada em variáveis de ambiente."""

    @staticmethod
    def get_provider(env: Optional[str] = None) -> EmbeddingProvider:
        current_env = env or os.getenv("ENVIRONMENT", "development").lower()
        provider_name = os.getenv("EMBEDDING_PROVIDER", "").lower()

        if current_env == "production":
            if not provider_name:
                raise ConfigurationError("EMBEDDING_PROVIDER não configurado no ambiente de produção. Fallback para Mock é estritamente proibido.")
            
            # Aqui podem ser instanciados adaptadores reais de produção (ex: OpenAIEmbeddingAdapter, etc.)
            raise ConfigurationError(f"Provedor de embedding de produção '{provider_name}' não disponível neste runtime.")
        
        # Em ambiente de desenvolvimento e testes, utiliza MockEmbeddingProvider controlado
        return MockEmbeddingProvider()
