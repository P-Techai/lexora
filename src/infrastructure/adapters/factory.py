import os
from typing import Optional

from src.application.ports.embedding_provider import EmbeddingProvider
from src.application.ports.legal_answer_generator import LegalAnswerGenerator
from src.domain.exceptions import ConfigurationError
from src.infrastructure.adapters.mock_embedding import MockEmbeddingProvider
from src.infrastructure.adapters.mock_legal_answer_generator import MockLegalAnswerGenerator


class EmbeddingProviderFactory:
    """Factory para instanciação de provedores de embedding baseada em variáveis de ambiente."""

    @staticmethod
    def get_provider(env: Optional[str] = None) -> EmbeddingProvider:
        current_env = env or os.getenv("ENVIRONMENT", "development").lower()
        provider_name = os.getenv("EMBEDDING_PROVIDER", "").lower()

        if current_env == "production":
            if not provider_name:
                raise ConfigurationError("EMBEDDING_PROVIDER não configurado no ambiente de produção. Fallback para Mock é estritamente proibido.")
            
            raise ConfigurationError(f"Provedor de embedding de produção '{provider_name}' não disponível neste runtime.")
        
        return MockEmbeddingProvider()


class LegalAnswerGeneratorFactory:
    """Factory para instanciação determinística do gerador de respostas jurídicas baseada em ambiente."""

    @staticmethod
    def get_generator(env: Optional[str] = None) -> LegalAnswerGenerator:
        current_env = env or os.getenv("ENVIRONMENT", "development").lower()
        provider_name = os.getenv("LEGAL_ANSWER_PROVIDER", "mock").lower()

        if current_env == "production":
            if not provider_name or provider_name == "mock":
                raise ConfigurationError("LEGAL_ANSWER_PROVIDER não configurado ou definido como 'mock' em ambiente de produção. Fallback para Mock é estritamente proibido.")
            
            raise ConfigurationError(f"Provedor de geração de produção '{provider_name}' não suportado neste runtime.")
        
        if provider_name != "mock":
            raise ConfigurationError(f"Provedor de geração '{provider_name}' não reconhecido.")

        return MockLegalAnswerGenerator()
