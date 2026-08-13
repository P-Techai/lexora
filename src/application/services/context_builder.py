import uuid
from typing import List, Optional

from src.application.dto.context_pack import LegalContextPack
from src.application.dto.retrieval_dto import LegalRetrievalResultItem, LegalRetrievalResultResponse
from src.domain.exceptions import ContextBudgetExceededError


class LegalContextBuilder:
    """Construtor determinístico de pacote de contexto (LegalContextPack) com controle rígido de orçamento."""

    def __init__(self, max_nodes: int = 10, max_characters: int = 15000):
        self.max_nodes = max_nodes
        self.max_characters = max_characters

    def build_context_pack(
        self,
        retrieval_response: LegalRetrievalResultResponse,
        max_results_override: Optional[int] = None
    ) -> LegalContextPack:
        """Monta o contexto fechado selecionando os candidatos ranqueados até o limite configurado."""
        effective_max_nodes = min(max_results_override or self.max_nodes, self.max_nodes)
        
        candidates = retrieval_response.results
        selected_nodes: List[LegalRetrievalResultItem] = []
        seen_node_ids = set()

        context_lines = [
            f"DATA DE REFERÊNCIA TEMPORAL DA CONSULTA: {retrieval_response.reference_date}",
            f"CONSULTA: {retrieval_response.query}",
            "--- DISPOSITIVOS NORMATIVOS VIGENTES RECUPERADOS ---"
        ]

        total_chars = sum(len(line) for line in context_lines)

        for item in candidates:
            if len(selected_nodes) >= effective_max_nodes:
                break

            if item.legal_node_id in seen_node_ids:
                continue

            node_block = (
                f"\n[EVIDÊNCIA ID: {item.evidence_id} | NÓ ID: {item.legal_node_id}]\n"
                f"HIERARQUIA: {item.hierarchical_context}\n"
                f"DISPOSITIVO: {item.label}\n"
                f"TEXTO: {item.text}\n"
                f"VIGÊNCIA: {item.effective_from or 'INÍCIO'} a {item.effective_until or 'VIGENTE'}\n"
                f"FONTE ID: {item.source_id} | RAW HASH: {item.content_hash}\n"
            )

            if total_chars + len(node_block) > self.max_characters:
                break

            selected_nodes.append(item)
            seen_node_ids.add(item.legal_node_id)
            context_lines.append(node_block)
            total_chars += len(node_block)

        canonical_text = "\n".join(context_lines)
        pack_id = f"pack-{uuid.uuid4().hex[:12]}"

        provenance_summary = {
            "retrieved_count": len(candidates),
            "selected_count": len(selected_nodes),
            "provenance_valid": retrieval_response.provenance_valid
        }

        return LegalContextPack(
            pack_id=pack_id,
            query=retrieval_response.query,
            normalized_query=retrieval_response.normalized_query,
            reference_date=retrieval_response.reference_date,
            retrieval_results=candidates,
            selected_nodes=selected_nodes,
            canonical_context_text=canonical_text,
            provenance_summary=provenance_summary,
            total_characters=total_chars
        )
