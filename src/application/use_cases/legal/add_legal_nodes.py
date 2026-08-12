from typing import List

from src.application.ports.repositories import LegalNodeRepository, LegalVersionRepository
from src.domain.entities.legal_node import LegalNode
from src.domain.exceptions import InvalidLegalDocumentError
from src.domain.services.tree_validator import LegalTreeIntegrityValidator


class AddLegalNodesUseCase:
    """Caso de uso para validar integridade estrutural e persistir nós em lote."""

    def __init__(self, node_repo: LegalNodeRepository, version_repo: LegalVersionRepository):
        self.node_repo = node_repo
        self.version_repo = version_repo

    async def execute(self, legal_version_id: str, nodes: List[LegalNode]) -> List[LegalNode]:
        version = await self.version_repo.get_by_id(legal_version_id)
        if not version:
            raise InvalidLegalDocumentError(f"LegalVersion com ID '{legal_version_id}' não existe.")

        # Validação pura de integridade da árvore (versão, ciclos, ordenação)
        LegalTreeIntegrityValidator.validate_tree(nodes, expected_version_id=legal_version_id)

        await self.node_repo.save_bulk(nodes)
        return nodes
