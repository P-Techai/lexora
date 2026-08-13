import uuid
from datetime import datetime, timezone
from typing import List

from src.application.dto.context_pack import LegalContextPack
from src.domain.entities.legal_answer import LegalAnswer
from src.domain.enums import LegalAnswerStatus


class AbstentionPolicy:
    """Política determinística de abstenção quando a evidência é insuficiente ou ocorrem conflitos insuperáveis."""

    @staticmethod
    def generate_abstention_answer(
        context_pack: LegalContextPack,
        status: LegalAnswerStatus = LegalAnswerStatus.INSUFFICIENT_EVIDENCE,
        reason: str = "Não foi encontrada evidência normativa suficiente para responder com segurança na data informada."
    ) -> LegalAnswer:
        """Gera uma resposta estruturada de abstenção mantendo a auditoria sem inventar dados."""
        answer_id = f"ans-abs-{uuid.uuid4().hex[:12]}"
        
        return LegalAnswer(
            answer_id=answer_id,
            query=context_pack.query,
            reference_date=context_pack.reference_date,
            answer_text=f"ABSTENÇÃO NORMATIVA: {reason}",
            confidence=0.0,
            status=status,
            citations=[],
            supporting_nodes=[],
            provenance=context_pack.provenance_summary,
            warnings=context_pack.warnings,
            conflicts=context_pack.conflicts + [reason],
            abstained=True,
            generated_at=datetime.now(timezone.utc)
        )
