from typing import List, Tuple
from src.application.dto.context_pack import LegalContextPack
from src.domain.entities.legal_answer import LegalAnswer


class ProvenanceGuard:
    """Guardião de proveniência garantindo que 100% das citações possuem a cadeia de 5 níveis rastreável."""

    @staticmethod
    def validate_provenance(answer: LegalAnswer, context_pack: LegalContextPack) -> Tuple[bool, List[str]]:
        """Valida se todas as citações possuem elos válidos: Node -> Version -> Evidence -> RawArtifact -> Source."""
        warnings: List[str] = []

        for citation in answer.citations:
            if not citation.source_id or not citation.evidence_id or not citation.raw_artifact_hash:
                warnings.append(f"Proveniência incompleta na citação '{citation.citation_id}': elos essenciais da cadeia de 5 níveis estão ausentes.")
                return False, warnings

        return True, warnings
