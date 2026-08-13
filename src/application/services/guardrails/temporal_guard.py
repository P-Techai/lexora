from typing import List, Tuple
from src.application.dto.context_pack import LegalContextPack
from src.domain.entities.legal_answer import LegalAnswer
from src.domain.services.temporal_validator import TemporalIntegrityValidator


class TemporalAnswerGuard:
    """Guardião temporal garantindo que nenhuma citação viole a vigência na data de referência solicitada."""

    @staticmethod
    def validate_temporal_integrity(answer: LegalAnswer, context_pack: LegalContextPack) -> Tuple[bool, List[str]]:
        """Valida que todas as citações e nós de suporte são temporalmente vigentes na reference_date."""
        ref_date = context_pack.reference_date
        warnings: List[str] = []

        for citation in answer.citations:
            is_effective = TemporalIntegrityValidator.is_date_in_range(
                target_date=ref_date,
                effective_from=citation.effective_from,
                effective_until=citation.effective_until
            )

            if not is_effective:
                warnings.append(f"Violação Temporal na citação '{citation.identifier}': o dispositivo não estava vigente na data de referência {ref_date}.")
                return False, warnings

        return True, warnings
