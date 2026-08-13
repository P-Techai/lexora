from typing import List, Tuple
from src.application.dto.context_pack import LegalContextPack
from src.domain.entities.legal_answer import LegalAnswer, LegalCitation


class CitationValidator:
    """Validador rigoroso de citações jurídicas contra o LegalContextPack fornecido."""

    @staticmethod
    def validate_citations(answer: LegalAnswer, context_pack: LegalContextPack) -> Tuple[bool, List[str]]:
        """
        Confirma que todas as citações da resposta possuem correspondência exata
        com os nós do contexto. Detecta citações inventadas ou não fundamentadas.
        """
        valid_node_ids = {node.legal_node_id for node in context_pack.selected_nodes}
        warnings: List[str] = []

        if not answer.citations and context_pack.selected_nodes:
            warnings.append("Resposta sem citações formais apesar de haver contexto normativo disponível.")

        for citation in answer.citations:
            # Check 1: Nó existe no contexto?
            if citation.legal_node_id not in valid_node_ids:
                warnings.append(f"Citação inválida/inventada detectada: nó ID '{citation.legal_node_id}' não pertence ao contexto de evidências.")
                return False, warnings

            # Check 2: Evidence ID válido?
            matching_item = next((n for n in context_pack.selected_nodes if n.legal_node_id == citation.legal_node_id), None)
            if matching_item and citation.evidence_id != matching_item.evidence_id:
                warnings.append(f"Inconsistência de Evidência na citação '{citation.citation_id}': Evidence ID '{citation.evidence_id}' diverge do contexto.")
                return False, warnings

        return True, warnings
