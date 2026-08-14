from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import ReviewReason, ReviewStatus
from src.domain.fiscal.fiscal_review import FiscalReview, ReviewEvent
from src.infrastructure.db.models.postgres_copilot_models import (
    FiscalReviewEventModel,
    FiscalReviewModel,
)


class PostgresFiscalReviewRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_review(self, review: FiscalReview) -> FiscalReview:
        stmt = select(FiscalReviewModel).where(FiscalReviewModel.review_id == review.review_id)
        res = await self.session.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            existing.status = review.status.value
            existing.assigned_to = review.assigned_to
            existing.updated_at = datetime.utcnow()
        else:
            model = FiscalReviewModel(
                review_id=review.review_id,
                decision_id=review.decision_id,
                status=review.status.value,
                reason=review.reason.value,
                description=review.description,
                assigned_to=review.assigned_to,
            )
            self.session.add(model)

        await self.session.flush()
        return review

    async def get_review_by_id(self, review_id: str) -> Optional[FiscalReview]:
        stmt = select(FiscalReviewModel).where(FiscalReviewModel.review_id == review_id)
        res = await self.session.execute(stmt)
        m = res.scalar_one_or_none()
        if not m:
            return None
        return FiscalReview(
            review_id=m.review_id,
            decision_id=m.decision_id,
            status=ReviewStatus(m.status),
            reason=ReviewReason(m.reason),
            description=m.description,
            assigned_to=m.assigned_to,
            created_at=m.created_at.isoformat(),
            updated_at=m.updated_at.isoformat(),
        )

    async def list_reviews(
        self,
        status: Optional[ReviewStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[FiscalReview]:
        stmt = select(FiscalReviewModel)
        if status:
            stmt = stmt.where(FiscalReviewModel.status == status.value)
        stmt = stmt.order_by(FiscalReviewModel.created_at.desc()).limit(limit).offset(offset)

        res = await self.session.execute(stmt)
        models = res.scalars().all()
        return [
            FiscalReview(
                review_id=m.review_id,
                decision_id=m.decision_id,
                status=ReviewStatus(m.status),
                reason=ReviewReason(m.reason),
                description=m.description,
                assigned_to=m.assigned_to,
                created_at=m.created_at.isoformat(),
                updated_at=m.updated_at.isoformat(),
            )
            for m in models
        ]

    async def save_review_event(self, event: ReviewEvent) -> ReviewEvent:
        model = FiscalReviewEventModel(
            event_id=event.event_id,
            review_id=event.review_id,
            decision_id=event.decision_id,
            actor_id=event.actor_id,
            action=event.action,
            reason=event.reason,
            previous_state=event.previous_state.value,
            new_state=event.new_state.value,
            evidence_reference=event.evidence_reference,
            event_hash=event.event_hash,
        )
        self.session.add(model)
        await self.session.flush()
        return event

    async def list_events_for_review(self, review_id: str) -> List[ReviewEvent]:
        stmt = select(FiscalReviewEventModel).where(
            FiscalReviewEventModel.review_id == review_id
        ).order_by(FiscalReviewEventModel.timestamp.asc())

        res = await self.session.execute(stmt)
        models = res.scalars().all()
        return [
            ReviewEvent(
                event_id=m.event_id,
                review_id=m.review_id,
                decision_id=m.decision_id,
                actor_id=m.actor_id,
                action=m.action,
                reason=m.reason,
                previous_state=ReviewStatus(m.previous_state),
                new_state=ReviewStatus(m.new_state),
                timestamp=m.timestamp.isoformat(),
                evidence_reference=m.evidence_reference,
                event_hash=m.event_hash,
            )
            for m in models
        ]
