import json
import uuid
from typing import List, Optional

from src.application.ports.embedding_provider import EmbeddingProvider
from src.application.ports.repositories import LegalNodeRepository, LegalVersionRepository
from src.domain.entities.legal_embedding import LegalEmbedding
from src.domain.entities.legal_node import LegalNode
from src.domain.services.retrieval_text_builder import CanonicalRetrievalTextBuilder


class LegalEmbeddingIndexer:
    """Serviço de indexação de dispositivos normativos (LegalNode) gerando embeddings canônicos."""

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        node_repo: LegalNodeRepository,
        version_repo: LegalVersionRepository
    ):
        self.embedding_provider = embedding_provider
        self.node_repo = node_repo
        self.version_repo = version_repo

    async def index_node(self, node: LegalNode, ancestors: Optional[List[LegalNode]] = None) -> LegalEmbedding:
        """Indexa um nó normativo construindo seu texto canônico com contexto hierárquico e gerando o vetor de embedding."""
        canonical_text = CanonicalRetrievalTextBuilder.build_retrieval_text(node, ancestors)
        vector = await self.embedding_provider.get_embedding(canonical_text)

        version = await self.version_repo.get_by_id(node.legal_version_id)
        doc_id = version.legal_document_id if version else "doc-unknown"

        embedding_id = f"emb-{uuid.uuid4().hex[:12]}"
        
        return LegalEmbedding(
            id=embedding_id,
            legal_node_id=node.id,
            legal_version_id=node.legal_version_id,
            legal_document_id=doc_id,
            content_hash=node.content_hash,
            embedding_model=self.embedding_provider.model_name,
            embedding_model_version=self.embedding_provider.model_version,
            dimensions=self.embedding_provider.dimensions,
            vector=vector
        )
