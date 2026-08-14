from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.enums import ClassificationStatus, TaxType
from src.domain.fiscal.calculation_memory import CalculationMemory
from src.domain.fiscal.fiscal_product_profile import FiscalProductProfile
from src.infrastructure.db.models.postgres_classification_models import (
    FiscalCalculationMemoryModel,
    FiscalProductProfileModel,
)


class PostgresClassificationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_product_profile(self, profile: FiscalProductProfile) -> FiscalProductProfile:
        stmt = select(FiscalProductProfileModel).where(FiscalProductProfileModel.product_id == profile.product_id)
        res = await self.session.execute(stmt)
        m = res.scalar_one_or_none()

        if m:
            m.ncm = profile.ncm
            m.cest = profile.cest
            m.fiscal_status = profile.fiscal_status.value
            m.classification_confidence = profile.classification_confidence
            m.classification_source = profile.classification_source
        else:
            m = FiscalProductProfileModel(
                product_id=profile.product_id,
                sku=profile.sku,
                gtin=profile.gtin,
                description=profile.description,
                normalized_description=profile.normalized_description,
                ncm=profile.ncm,
                cest=profile.cest,
                unit=profile.unit,
                origin=str(profile.origin),
                fiscal_status=profile.fiscal_status.value,
                classification_confidence=profile.classification_confidence,
                classification_source=profile.classification_source
            )
            self.session.add(m)

        await self.session.flush()
        return profile

    async def get_product_profile_by_id(self, product_id: str) -> Optional[FiscalProductProfile]:
        stmt = select(FiscalProductProfileModel).where(FiscalProductProfileModel.product_id == product_id)
        res = await self.session.execute(stmt)
        m = res.scalar_one_or_none()
        if not m:
            return None
        return FiscalProductProfile(
            product_id=m.product_id,
            sku=m.sku,
            gtin=m.gtin,
            description=m.description,
            normalized_description=m.normalized_description,
            ncm=m.ncm,
            cest=m.cest,
            unit=m.unit,
            origin=int(m.origin),
            fiscal_status=ClassificationStatus(m.fiscal_status),
            classification_confidence=float(m.classification_confidence),
            classification_source=m.classification_source
        )

    async def save_calculation_memory(self, memory: CalculationMemory) -> CalculationMemory:
        m = FiscalCalculationMemoryModel(
            calculation_id=memory.calculation_id,
            operation_id=memory.operation_id,
            item_id=memory.item_id,
            tax_type=memory.tax_type.value,
            taxable_base=memory.taxable_base,
            rate=memory.rate,
            calculated_amount=memory.calculated_amount,
            inputs=memory.inputs,
            formula=memory.formula,
            rounding_policy=memory.rounding_policy,
            rule_id=memory.rule_id,
            legal_reference=memory.legal_reference,
            evidence_id=memory.evidence_id,
            memory_hash=memory.memory_hash
        )
        self.session.add(m)
        await self.session.flush()
        return memory

    async def get_calculation_memory_by_id(self, calculation_id: str) -> Optional[CalculationMemory]:
        stmt = select(FiscalCalculationMemoryModel).where(FiscalCalculationMemoryModel.calculation_id == calculation_id)
        res = await self.session.execute(stmt)
        m = res.scalar_one_or_none()
        if not m:
            return None
        return CalculationMemory(
            calculation_id=m.calculation_id,
            operation_id=m.operation_id,
            item_id=m.item_id,
            tax_type=TaxType(m.tax_type),
            taxable_base=m.taxable_base,
            rate=m.rate,
            calculated_amount=m.calculated_amount,
            inputs=m.inputs,
            formula=m.formula,
            rounding_policy=m.rounding_policy,
            rule_id=m.rule_id,
            legal_reference=m.legal_reference,
            evidence_id=m.evidence_id,
            calculated_at=m.calculated_at.isoformat(),
            memory_hash=m.memory_hash
        )
