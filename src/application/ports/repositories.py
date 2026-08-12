from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from src.domain.entities.evidence import Evidence
from src.domain.entities.legal_document import LegalDocument
from src.domain.entities.legal_node import LegalNode
from src.domain.entities.legal_relation import LegalRelation
from src.domain.entities.legal_version import LegalVersion
from src.domain.entities.source import Source
from src.domain.enums import DocumentType, Jurisdiction


class SourceRepository(ABC):
    """Porta de repositório para persistência da entidade Source."""

    @abstractmethod
    async def get_by_id(self, source_id: str) -> Optional[Source]:
        pass

    @abstractmethod
    async def save(self, source: Source) -> Source:
        pass

    @abstractmethod
    async def list_active(self) -> List[Source]:
        pass


class LegalDocumentRepository(ABC):
    """Porta de repositório para a unidade documental LegalDocument."""

    @abstractmethod
    async def get_by_id(self, document_id: str) -> Optional[LegalDocument]:
        pass

    @abstractmethod
    async def find_by_number_and_type(
        self,
        document_number: str,
        document_type: DocumentType,
        jurisdiction: Jurisdiction
    ) -> List[LegalDocument]:
        pass

    @abstractmethod
    async def save(self, document: LegalDocument) -> LegalDocument:
        pass


class LegalVersionRepository(ABC):
    """Porta de repositório para versões históricas LegalVersion."""

    @abstractmethod
    async def get_by_id(self, version_id: str) -> Optional[LegalVersion]:
        pass

    @abstractmethod
    async def get_effective_version(self, document_id: str, target_date: date) -> Optional[LegalVersion]:
        """Obtém a versão que estava juridicamente vigente em uma data específica."""
        pass

    @abstractmethod
    async def save(self, version: LegalVersion) -> LegalVersion:
        pass


class LegalNodeRepository(ABC):
    """Porta de repositório para os nós estruturais LegalNode."""

    @abstractmethod
    async def get_by_id(self, node_id: str) -> Optional[LegalNode]:
        pass

    @abstractmethod
    async def get_children(self, parent_id: str) -> List[LegalNode]:
        """Recupera os nós filhos diretos ordenados por position."""
        pass

    @abstractmethod
    async def get_tree_by_version(self, version_id: str) -> List[LegalNode]:
        """Recupera todos os nós pertencentes a uma versão ordenados hierarquicamente."""
        pass

    @abstractmethod
    async def save(self, node: LegalNode) -> LegalNode:
        pass

    @abstractmethod
    async def save_bulk(self, nodes: List[LegalNode]) -> None:
        pass


class LegalRelationRepository(ABC):
    """Porta de repositório para relações normativas LegalRelation."""

    @abstractmethod
    async def get_by_id(self, relation_id: str) -> Optional[LegalRelation]:
        pass

    @abstractmethod
    async def get_relations_from(self, source_node_id: str) -> List[LegalRelation]:
        pass

    @abstractmethod
    async def get_relations_to(self, target_node_id: str) -> List[LegalRelation]:
        pass

    @abstractmethod
    async def save(self, relation: LegalRelation) -> LegalRelation:
        pass


class EvidenceRepository(ABC):
    """Porta de repositório para registros de evidências documental Evidence."""

    @abstractmethod
    async def get_by_id(self, evidence_id: str) -> Optional[Evidence]:
        pass

    @abstractmethod
    async def get_by_hash(self, content_hash: str) -> Optional[Evidence]:
        pass

    @abstractmethod
    async def save(self, evidence: Evidence) -> Evidence:
        pass
