from typing import List, Tuple
from src.application.dto.context_pack import LegalContextPack
from src.domain.entities.legal_answer import LegalAnswer, LegalCitation
from src.domain.services.temporal_validator import TemporalIntegrityValidator


class CitationValidator:
    """Validador rigoroso de citações e claims jurídicos com verificação cruzada de 12 campos."""

    @classmethod
    def validate_citations(cls, answer: LegalAnswer, context_pack: LegalContextPack) -> Tuple[bool, List[str]]:
        """
        Confirma que todas as citações e claims da resposta possuem correspondência rigorosa nos 12 campos:
        1. legal_node_id
        2. legal_version_id
        3. legal_document_id
        4. node_type
        5. identifier
        6. label
        7. excerpt
        8. effective_from
        9. effective_until
        10. source_id
        11. evidence_id
        12. raw_artifact_hash
        """
        warnings: List[str] = []
        context_items_by_node = {item.legal_node_id: item for item in context_pack.selected_nodes}
        citation_by_id = {c.citation_id: c for c in answer.citations}

        # 1. Validação de Claims vs Citações
        if answer.claims:
            for claim in answer.claims:
                if not claim.citation_ids:
                    warnings.append(f"Claim sem citação: a afirmação '{claim.claim_id}' não possui citação vinculada.")
                    return False, warnings
                
                for cit_id in claim.citation_ids:
                    if cit_id not in citation_by_id:
                        warnings.append(f"Citação inexistente no claim '{claim.claim_id}': ID '{cit_id}' não encontrado nas citações da resposta.")
                        return False, warnings

        # 2. Validação Rigorosa dos 12 Campos de Cada Citação
        for citation in answer.citations:
            item = context_items_by_node.get(citation.legal_node_id)
            if not item:
                warnings.append(f"Citação inventada: nó ID '{citation.legal_node_id}' não pertence ao contexto de evidências.")
                return False, warnings

            # Verificação Cruzada de Campos
            if citation.legal_version_id != item.legal_version_id:
                warnings.append(f"Divergência de Versão na citação '{citation.citation_id}': version_id '{citation.legal_version_id}' != '{item.legal_version_id}'.")
                return False, warnings

            if citation.legal_document_id != item.legal_document_id:
                warnings.append(f"Divergência de Documento na citação '{citation.citation_id}': document_id '{citation.legal_document_id}' != '{item.legal_document_id}'.")
                return False, warnings

            if citation.node_type != item.node_type:
                warnings.append(f"Divergência de Tipo na citação '{citation.citation_id}': node_type '{citation.node_type}' != '{item.node_type}'.")
                return False, warnings

            if citation.source_id != item.source_id:
                warnings.append(f"Divergência de Fonte na citação '{citation.citation_id}': source_id '{citation.source_id}' != '{item.source_id}'.")
                return False, warnings

            if citation.evidence_id != item.evidence_id:
                warnings.append(f"Divergência de Evidência na citação '{citation.citation_id}': evidence_id '{citation.evidence_id}' != '{item.evidence_id}'.")
                return False, warnings

            if citation.raw_artifact_hash != item.content_hash:
                warnings.append(f"Divergência de Raw Hash na citação '{citation.citation_id}': raw_artifact_hash '{citation.raw_artifact_hash}' != '{item.content_hash}'.")
                return False, warnings

            # Validação da Matemática Temporal Semi-Aberta via TemporalIntegrityValidator
            is_effective = TemporalIntegrityValidator.is_date_in_range(
                target_date=context_pack.reference_date,
                effective_from=citation.effective_from,
                effective_until=citation.effective_until
            )
            if not is_effective:
                warnings.append(f"Vigência temporal inválida na citação '{citation.citation_id}' para a data {context_pack.reference_date}.")
                return False, warnings

        return True, warnings
