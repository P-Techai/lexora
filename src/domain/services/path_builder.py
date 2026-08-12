from typing import Dict, Optional
from src.domain.entities.legal_node import LegalNode


class LegalNodePathBuilder:
    """Constroi caminhos estruturais determinísticos para os nós da árvore normativa sem dependências de banco."""

    @staticmethod
    def build_path(identifier: str, parent: Optional[LegalNode] = None) -> str:
        """Gera o caminho absoluto padronizado. Ex: '/art-1/par-1/inc-1'."""
        clean_ident = identifier.strip().lower().replace(" ", "-").replace(".", "")

        if parent is None or not parent.path:
            return f"/{clean_ident}"

        parent_path = parent.path.rstrip("/")
        return f"{parent_path}/{clean_ident}"

    @staticmethod
    def rebuild_all_paths(nodes: list[LegalNode]) -> Dict[str, str]:
        """Reconstrói os caminhos determinísticos para uma lista de nós pertencentes a uma mesma árvore."""
        nodes_by_id = {node.id: node for node in nodes}
        updated_paths: Dict[str, str] = {}

        def resolve_node_path(node: LegalNode) -> str:
            if node.id in updated_paths:
                return updated_paths[node.id]

            if node.parent_id is None or node.parent_id not in nodes_by_id:
                path = LegalNodePathBuilder.build_path(node.identifier, parent=None)
            else:
                parent_node = nodes_by_id[node.parent_id]
                parent_path = resolve_node_path(parent_node)
                # mock parent com path atualizado
                dummy_parent = parent_node.model_copy(update={"path": parent_path})
                path = LegalNodePathBuilder.build_path(node.identifier, parent=dummy_parent)

            updated_paths[node.id] = path
            return path

        for node in nodes:
            resolve_node_path(node)

        return updated_paths
