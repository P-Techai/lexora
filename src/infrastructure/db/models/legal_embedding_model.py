from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.base import Base


class LegalEmbeddingModel(Base):
    __tablename__ = "legal_node_embeddings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    legal_node_id: Mapped[str] = mapped_column(String(36), ForeignKey("legal_nodes.id", ondelete="RESTRICT"), nullable=False)
    legal_version_id: Mapped[str] = mapped_column(String(36), ForeignKey("legal_versions.id", ondelete="RESTRICT"), nullable=False)
    legal_document_id: Mapped[str] = mapped_column(String(36), ForeignKey("legal_documents.id", ondelete="RESTRICT"), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    embedding_model: Mapped[str] = mapped_column(String(100), nullable=False)
    embedding_model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    dimensions: Mapped[int] = mapped_column(Integer, nullable=False)
    vector_data: Mapped[str] = mapped_column(Text, nullable=False)  # JSON/CSV de floats para compatibilidade com pgvector
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint("legal_node_id", "content_hash", "embedding_model", "embedding_model_version", name="uq_node_embedding_model"),
        Index("idx_embedding_node", "legal_node_id"),
        Index("idx_embedding_version", "legal_version_id"),
        Index("idx_embedding_document", "legal_document_id"),
    )
