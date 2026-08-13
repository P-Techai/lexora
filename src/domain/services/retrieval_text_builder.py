from typing import List, Optional
from src.domain.entities.legal_node import LegalNode


class CanonicalRetrievalTextBuilder:
    """Construtor determinístico de texto canônico de recuperação agregando a hierarquia normativa ancestral."""

    @staticmethod
    def build_retrieval_text(node: LegalNode, ancestors: Optional[List[LegalNode]] = None) -> str:
        """
        Constrói uma representação textual estruturada incorporando o contexto dos nós pais.
        Evita a perda de contexto ao indexar artigos ou incisos isoladamente.
        Exemplo: "[LEI COMPLEMENTAR 116/2003] CAPÍTULO I > Art. 1º § 1º O imposto incide também..."
        """
        if not ancestors:
            return f"[{node.label}] {node.text}".strip()

        # Ordena os ancestrais pela posição/profundidade (menor posição -> raiz)
        sorted_ancestors = sorted(ancestors, key=lambda n: n.position)

        context_parts = []
        for anc in sorted_ancestors:
            if anc.id != node.id:
                context_parts.append(f"{anc.label}")

        context_str = " > ".join(context_parts)
        if context_str:
            return f"[{context_str}] {node.label}: {node.text}".strip()

        return f"[{node.label}] {node.text}".strip()
