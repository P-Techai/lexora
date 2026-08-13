from typing import List, Tuple
from src.application.dto.context_pack import LegalContextPack


class ConflictGuard:
    """Guardião de conflitos e lacunas normativas (Temporal Conflicts, Temporal Gaps, Conflicting Sources)."""

    @staticmethod
    def detect_conflicts(context_pack: LegalContextPack) -> Tuple[bool, List[str]]:
        """Detecta se há ambiguidades estruturais ou conflitos entre versões no contexto fornecido."""
        conflicts: List[str] = []

        if not context_pack.selected_nodes:
            conflicts.append("Nenhum dispositivo normativo localizado para a data de referência.")
            return True, conflicts

        # Detecta se há versões conflitantes do mesmo documento no mesmo contexto
        document_versions = {}
        for node in context_pack.selected_nodes:
            doc_id = node.legal_document_id
            ver_id = node.legal_version_id
            if doc_id in document_versions and document_versions[doc_id] != ver_id:
                conflicts.append(f"Conflito de Versões: o contexto contém dispositivos de versões distintas ({ver_id} e {document_versions[doc_id]}) do documento '{doc_id}'.")
            else:
                document_versions[doc_id] = ver_id

        has_conflicts = len(conflicts) > 0
        return has_conflicts, conflicts
