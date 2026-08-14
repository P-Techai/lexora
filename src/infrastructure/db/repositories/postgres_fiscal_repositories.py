from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.fiscal_rule_repository import FiscalTaxRuleRepository
from src.domain.enums import Jurisdiction, TaxType
from src.domain.exceptions import DuplicateNFeError
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule
from src.infrastructure.db.models.postgres_fiscal_models import (
    FiscalCalculationLogModel,
    FiscalDecisionModel,
    FiscalTaxRuleModel,
    NFeDocumentModel,
    NFeItemModel,
)


class PostgresFiscalTaxRuleRepository(FiscalTaxRuleRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_rule(self, rule: FiscalTaxRule) -> FiscalTaxRule:
        model = FiscalTaxRuleModel(
            rule_id=rule.rule_id,
            tax_type=rule.tax_type.value,
            jurisdiction=rule.jurisdiction.value,
            state=rule.state,
            municipality=rule.municipality,
            effective_from=rule.effective_from,
            effective_until=rule.effective_until,
            priority=rule.priority,
            formula=rule.formula,
            rate=rule.rate,
            base_reduction=rule.base_reduction,
            is_exempt=rule.is_exempt,
            has_benefit=rule.has_benefit,
            source_legal_node_id=rule.source_legal_node_id,
            source_legal_version_id=rule.source_legal_version_id,
            evidence_id=rule.evidence_id,
            rule_version=rule.rule_version,
            status=rule.status,
            conditions=rule.conditions,
        )
        self.session.add(model)
        await self.session.flush()
        return rule

    async def get_rule_by_id(self, rule_id: str) -> Optional[FiscalTaxRule]:
        stmt = select(FiscalTaxRuleModel).where(FiscalTaxRuleModel.rule_id == rule_id)
        result = await self.session.execute(stmt)
        m = result.scalar_one_or_none()
        if not m:
            return None
        return self._to_domain(m)

    async def get_active_rules_by_tax_type(self, tax_type: TaxType, reference_date: date) -> List[FiscalTaxRule]:
        stmt = select(FiscalTaxRuleModel).where(
            FiscalTaxRuleModel.tax_type == tax_type.value,
            FiscalTaxRuleModel.status == "ACTIVE",
            FiscalTaxRuleModel.effective_from <= reference_date,
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        rules = []
        for m in models:
            if m.effective_until is None or m.effective_until > reference_date:
                rules.append(self._to_domain(m))
        return rules

    async def list_all_active_rules(self, reference_date: date) -> List[FiscalTaxRule]:
        stmt = select(FiscalTaxRuleModel).where(
            FiscalTaxRuleModel.status == "ACTIVE",
            FiscalTaxRuleModel.effective_from <= reference_date,
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        rules = []
        for m in models:
            if m.effective_until is None or m.effective_until > reference_date:
                rules.append(self._to_domain(m))
        return rules

    def _to_domain(self, m: FiscalTaxRuleModel) -> FiscalTaxRule:
        return FiscalTaxRule(
            rule_id=m.rule_id,
            tax_type=TaxType(m.tax_type),
            jurisdiction=Jurisdiction(m.jurisdiction),
            state=m.state,
            municipality=m.municipality,
            effective_from=m.effective_from,
            effective_until=m.effective_until,
            priority=m.priority,
            conditions=m.conditions or {},
            formula=m.formula,
            rate=Decimal(str(m.rate)),
            base_reduction=Decimal(str(m.base_reduction)),
            is_exempt=m.is_exempt,
            has_benefit=m.has_benefit,
            source_legal_node_id=m.source_legal_node_id,
            source_legal_version_id=m.source_legal_version_id,
            evidence_id=m.evidence_id,
            rule_version=m.rule_version,
            status=m.status,
        )


class PostgresNFeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_nfe(self, doc_model: NFeDocumentModel, items: List[NFeItemModel]):
        try:
            self.session.add(doc_model)
            for item in items:
                self.session.add(item)
            await self.session.flush()
        except IntegrityError as e:
            await self.session.rollback()
            raise DuplicateNFeError(
                f"NFe com chave de acesso '{doc_model.access_key}' ou hash XML '{doc_model.raw_xml_hash}' já cadastrada."
            ) from e
