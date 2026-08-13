from datetime import datetime, timezone
import hashlib
from typing import List

from src.application.dto.context_pack import LegalContextPack
from src.application.ports.legal_answer_generator import LegalAnswerGenerator
from src.domain.entities.legal_answer import AnswerClaim, LegalAnswer, LegalCitation
from src.domain.enums import LegalAnswerStatus


class MockLegalAnswerGenerator(LegalAnswerGenerator):
    """Adaptador Mock para geração de respostas jurídicas estruturadas com claims e IDs determinísticos."""

    PROMPT_VERSION = "1.0.0"

    @property
    def provider_name(self) -> str:
        return "mock-legal-generator"

    @property
    def model_version(self) -> str:
        return "1.0.0"

    async def generate_answer(self, context_pack: LegalContextPack) -> LegalAnswer:
        # Geração de IDs determinísticos via SHA-256 (0 UUIDs aleatórios)
        id_payload = f"{context_pack.query}|{context_pack.reference_date}|{context_pack.pack_id}|{self.provider_name}|{self.model_version}"
        id_hash = hashlib.sha256(id_payload.encode("utf-8")).hexdigest()[:16]
        answer_id = f"ans-{id_hash}"
        logical_answer_id = f"log-ans-{id_hash}"

        now = datetime.now(timezone.utc)

        if not context_pack.selected_nodes:
            return LegalAnswer(
                answer_id=answer_id,
                logical_answer_id=logical_answer_id,
                query=context_pack.query,
                reference_date=context_pack.reference_date,
                answer_text="Não foi encontrada evidência normativa suficiente para responder com segurança na data informada.",
                claims=[],
                confidence=0.0,
                status=LegalAnswerStatus.INSUFFICIENT_EVIDENCE,
                citations=[],
                supporting_nodes=[],
                provenance=context_pack.provenance_summary,
                warnings=["Contexto sem dispositivos normativos selecionados."],
                abstained=True,
                provider_name=self.provider_name,
                model_name="mock-model",
                model_version=self.model_version,
                prompt_version=self.PROMPT_VERSION,
                generated_at=now
            )

        citations: List[LegalCitation] = []
        supporting_nodes: List[str] = []
        claims: List[AnswerClaim] = []
        answer_parts = [
            f"Com base exclusivamente na legislação vigente em {context_pack.reference_date}:"
        ]

        for idx, item in enumerate(context_pack.selected_nodes):
            supporting_nodes.append(item.legal_node_id)
            cit_id = f"cit-{item.legal_node_id[:8]}"

            safe_text = item.text.replace("\n", " ").strip()
            claim_text = f"Conforme o {item.label} ({item.hierarchical_context}): \"{safe_text}\"."
            answer_parts.append(f"- {claim_text}")

            claim = AnswerClaim(
                claim_id=f"claim-{idx+1}",
                text=claim_text,
                citation_ids=[cit_id]
            )
            claims.append(claim)

            citation = LegalCitation(
                citation_id=cit_id,
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
            logical_answer_id=logical_answer_id,
            query=context_pack.query,
            reference_date=context_pack.reference_date,
            answer_text=answer_text,
            claims=claims,
            confidence=0.95,
            status=LegalAnswerStatus.SUPPORTED,
            citations=citations,
            supporting_nodes=supporting_nodes,
            provenance=context_pack.provenance_summary,
            warnings=[],
            conflicts=[],
            abstained=False,
            provider_name=self.provider_name,
            model_name="mock-model",
            model_version=self.model_version,
            prompt_version=self.PROMPT_VERSION,
            generated_at=now
        )
