from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.domain.entities.legal_node import LegalNode


class DatabaseProvider(ABC):
    """Porta abstrata para persistência de dados relacionais e vetoriais."""

    @abstractmethod
    async def get_legal_node_by_id(self, node_id: str) -> Optional[LegalNode]:
        """Obtém um dispositivo normativo pelo seu ID único."""
        pass

    @abstractmethod
    async def save_legal_node(self, node: LegalNode) -> None:
        """Persiste ou atualiza um dispositivo normativo no banco de dados."""
        pass

    @abstractmethod
    async def search_legal_nodes(
        self,
        query: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[LegalNode]:
        """Busca dispositivos normativos por palavras-chave ou metadados."""
        pass
