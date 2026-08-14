import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional

from src.domain.enums import ReviewStatus
from src.domain.exceptions import LexoraDomainError
from src.domain.fiscal.fiscal_review import FiscalReview, ReviewEvent


class InvalidReviewStateTransitionError(LexoraDomainError):
    """Lançada ao tentar realizar transição inválida na máquina de estados de revisão humana."""
    pass


class ReviewStateMachine:
    """
    Máquina de estados determinística para o Workflow de Revisão Humana.
    Transições permitidas:
      OPEN -> IN_REVIEW
      IN_REVIEW -> APPROVED, REJECTED, ESCALATED
    """

    ALLOWED_TRANSITIONS = {
        ReviewStatus.OPEN: {ReviewStatus.IN_REVIEW},
        ReviewStatus.IN_REVIEW: {ReviewStatus.APPROVED, ReviewStatus.REJECTED, ReviewStatus.ESCALATED},
        ReviewStatus.APPROVED: set(),
        ReviewStatus.REJECTED: set(),
        ReviewStatus.ESCALATED: set(),
    }

    @classmethod
    def transition(
        cls,
        review: FiscalReview,
        target_status: ReviewStatus,
        actor_id: str,
        action: str,
        reason: str,
        evidence_reference: Optional[str] = None
    ) -> tuple[FiscalReview, ReviewEvent]:
        current_status = review.status

        # Validação de transição
        if target_status not in cls.ALLOWED_TRANSITIONS.get(current_status, set()):
            raise InvalidReviewStateTransitionError(
                f"Transição de estado inválida para revisão '{review.review_id}': De '{current_status.value}' para '{target_status.value}' não é permitida."
            )

        now_iso = datetime.now(timezone.utc).isoformat()

        # Cria nova revisão atualizada (imutável)
        updated_review = FiscalReview(
            review_id=review.review_id,
            decision_id=review.decision_id,
            status=target_status,
            reason=review.reason,
            description=review.description,
            assigned_to=actor_id if target_status == ReviewStatus.IN_REVIEW else review.assigned_to,
            created_at=review.created_at,
            updated_at=now_iso
        )

        # Hash SHA-256 do evento
        raw_event_data = f"{review.review_id}|{review.decision_id}|{actor_id}|{action}|{current_status.value}|{target_status.value}|{now_iso}"
        event_hash = hashlib.sha256(raw_event_data.encode("utf-8")).hexdigest()

        event = ReviewEvent(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            review_id=review.review_id,
            decision_id=review.decision_id,
            actor_id=actor_id,
            action=action,
            reason=reason,
            previous_state=current_status,
            new_state=target_status,
            timestamp=now_iso,
            evidence_reference=evidence_reference,
            event_hash=event_hash
        )

        return updated_review, event
