from typing import List, Tuple
from src.application.dto.context_pack import LegalContextPack
from src.application.services.guardrails.abstention_policy import AbstentionPolicy
from src.application.services.guardrails.citation_validator import CitationValidator
from src.application.services.guardrails.conflict_guard import ConflictGuard
from src.application.services.guardrails.provenance_guard import ProvenanceGuard
from src.application.services.guardrails.temporal_guard import TemporalAnswerGuard
from src.domain.entities.legal_answer import LegalAnswer
from src.domain.enums import LegalAnswerStatus


class LegalAnswerGuard:
    """Orquestrador Central de Guardrails Jurídicos e Validação de Resposta Linguística."""

    @classmethod
    def validate_and_enforce(cls, answer: LegalAnswer, context_pack: LegalContextPack) -> LegalAnswer:
        """
        Submete a resposta gerada a todas as etapas de validação:
        1. Conflitos/Gaps no contexto
        2. Validação de Citações contra o contexto (0 citações inventadas)
        3. Validação Temporal de Vigência na reference_date
        4. Validação da Cadeia de Proveniência em 5 Níveis
        
        Se qualquer validação falhar, aplica a Política de Abstenção/Rejeição determinística.
        """
        # 1. Checagem de Evidências no Contexto
        if not context_pack.selected_nodes:
            return AbstentionPolicy.generate_abstention_answer(
                context_pack=context_pack,
                status=LegalAnswerStatus.INSUFFICIENT_EVIDENCE,
                reason="Nenhum dispositivo normativo localizado na data de referência."
            )

        # 2. Checagem de Conflitos Normativos ou de Versão
        has_conflicts, conflicts = ConflictGuard.detect_conflicts(context_pack)
        if has_conflicts:
            return AbstentionPolicy.generate_abstention_answer(
                context_pack=context_pack,
                status=LegalAnswerStatus.CONFLICTING_SOURCES,
                reason=f"Conflito normativo localizado: {'; '.join(conflicts)}"
            )

        # 3. Validação de Citações
        citations_valid, cit_warnings = CitationValidator.validate_citations(answer, context_pack)
        if not citations_valid:
            return AbstentionPolicy.generate_abstention_answer(
                context_pack=context_pack,
                status=LegalAnswerStatus.INSUFFICIENT_EVIDENCE,
                reason=f"Falha de Validação de Citação: {'; '.join(cit_warnings)}"
            )

        # 4. Validação Temporal de Vigência
        temporal_valid, temp_warnings = TemporalAnswerGuard.validate_temporal_integrity(answer, context_pack)
        if not temporal_valid:
            return AbstentionPolicy.generate_abstention_answer(
                context_pack=context_pack,
                status=LegalAnswerStatus.TEMPORAL_CONFLICT,
                reason=f"Falha de Vigência Temporal: {'; '.join(temp_warnings)}"
            )

        # 5. Validação da Cadeia de Proveniência
        provenance_valid, prov_warnings = ProvenanceGuard.validate_provenance(answer, context_pack)
        if not provenance_valid:
            return AbstentionPolicy.generate_abstention_answer(
                context_pack=context_pack,
                status=LegalAnswerStatus.PROVENANCE_FAILURE,
                reason=f"Falha de Proveniência em 5 Níveis: {'; '.join(prov_warnings)}"
            )

        # Resposta 100% validada e suportada
        return answer
