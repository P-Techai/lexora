from typing import Dict, List, Set

from src.domain.entities.legal_node import LegalNode
from src.domain.exceptions import (
    InconsistentPositionError,
    InvalidLegalNodeError,
    TreeCycleDetectedError,
)


class LegalTreeIntegrityValidator:
    """Validador puro de domínio para integridade estrutural da árvore hierárquica de nós normativos."""

    @staticmethod
    def validate_tree(nodes: List[LegalNode], expected_version_id: str) -> None:
        """Valida se a lista de nós forma uma árvore válida e íntegra."""
        if not nodes:
            return

        nodes_by_id: Dict[str, LegalNode] = {}
        children_by_parent: Dict[Optional[str], List[LegalNode]] = {}

        # 1. Validação de versão e indexação por ID
        for node in nodes:
            if node.legal_version_id != expected_version_id:
                raise InvalidLegalNodeError(
                    f"Nó '{node.id}' pertence à versão '{node.legal_version_id}', mas era esperada '{expected_version_id}'."
                )

            if node.id in nodes_by_id:
                raise InvalidLegalNodeError(f"ID de nó duplicado encontrado: '{node.id}'.")

            nodes_by_id[node.id] = node
            parent_key = node.parent_id
            children_by_parent.setdefault(parent_key, []).append(node)

        # 2. Validação de detecção de ciclos (A -> B -> C -> A)
        for node in nodes:
            visited: Set[str] = set()
            curr: Optional[LegalNode] = node
            while curr is not None:
                if curr.id in visited:
                    raise TreeCycleDetectedError(
                        f"Ciclo detectado na hierarquia do nó '{node.id}' no nó ancestral '{curr.id}'."
                    )
                visited.add(curr.id)
                if curr.parent_id is not None:
                    if curr.parent_id not in nodes_by_id:
                        raise InvalidLegalNodeError(
                            f"Nó '{curr.id}' possui parent_id '{curr.parent_id}' que não existe na lista de nós da versão."
                        )
                    curr = nodes_by_id[curr.parent_id]
                else:
                    curr = None

        # 3. Validação de ordenação por position (rejeita duplicatas no mesmo nível)
        for parent_id, children in children_by_parent.items():
            seen_positions: Set[int] = set()
            for child in children:
                if child.position <= 0:
                    raise InconsistentPositionError(
                        f"Nó '{child.id}' possui posição inválida (não positiva): {child.position}."
                    )
                if child.position in seen_positions:
                    raise InconsistentPositionError(
                        f"Posição duplicada {child.position} detectada entre nós com parent_id '{parent_id}'."
                    )
                seen_positions.add(child.position)
