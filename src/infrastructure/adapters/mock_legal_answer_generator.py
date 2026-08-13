from datetime import datetime, timezone
import uuid
from typing import List

from src.application.dto.context_pack import LegalContextPack
from src.application.ports.legal_answer_generator import LegalAnswerGenerator
from src.domain.entities.legal_answer import LegalAnswer, LegalCitation
from src.domain.enums import LegalAnswerStatus


class MockLegalAnswerGenerator(LegalAnswerGenerator):
    """Adaptador Mock para geração de respostas jurídicas estruturadas com proteção contra Prompt Injection."""

    @property
    def provider_name(self) -> str:
        return "mock-legal-generator"

    @property
    def model_version(self) -> str:
        return "1.0.0"

    async def generate_answer(self, context_pack: LegalContextPack) -> LegalAnswer:
        answer_id = f"ans-{uuid.uuid4().hex[:12]}"
        now = datetime.now(timezone.utc)

        if not context_pack.selected_nodes:
            return LegalAnswer(
                answer_id=answer_id,
                query=context_pack.query,
                reference_date=context_pack.reference_date,
                answer_text="Não foi encontrada evidência normativa suficiente para responder com segurança na data informada.",
                confidence=0.0,
                status=LegalAnswerStatus.INSUFFICIENT_EVIDENCE,
                citations=[],
                supporting_nodes=[],
                provenance=context_pack.provenance_summary,
                warnings=["Contexto sem dispositivos normativos selecionados."],
                abstained=True,
                generated_at=now
            )

        citations: List[LegalCitation] = []
        supporting_nodes: List[str] = []
        answer_parts = [
            f"Com base exclusivamente na legislação vigente em {context_pack.reference_date}:"
        ]

        for idx, item in enumerate(context_pack.selected_nodes):
            supporting_nodes.append(item.legal_node_id)

            # Proteção contra Prompt Injection: Trata o texto do nó estritamente como DADOS (sem interpretar comandos)
            safe_text = item.text.replace("\n", " ").strip()
            
            answer_parts.append(
                f"- Conforme o {item.label} ({item.hierarchical_context}): \"{safe_text}\"."
            )

            citation = LegalCitation(
                citation_id=f"cit-{item.legal_node_id[:8]}",
                legal_node_id=item.legal_node_id,
                legal_version_id=item.legal_version_id,
                legal_document_id=item.legal_document_id,
                node_type=item.node_type,
                identifier=item.identifier,
                label=item.label,
                excerpt=safe_text[:200],
                effective_from=item.effective_from,
                effective_until=item.effective_until,
                source_id=item.source_id,
                evidence_id=item.evidence_id,
                raw_artifact_hash=item.content_hash
            )
            citations.append(citation)

        answer_text = "\n".join(answer_parts)

        return LegalAnswer(
            answer_id=answer_id,
            query=context_pack.query,
            reference_date=context_pack.reference_date,
            answer_text=answer_text,
            confidence=0.95,
            status=LegalAnswerStatus.SUPPORTED,
            citations=citations,
            supporting_nodes=supporting_nodes,
            provenance=context_pack.provenance_summary,
            warnings=[],
            conflicts=[],
            abstained=False,
            generated_at=now
        )
