import hashlib
from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import Jurisdiction, TaxType
from src.domain.fiscal.fiscal_tax_rule import FiscalTaxRule


class FiscalRuleEvidence(BaseModel):
    model_config = ConfigDict(frozen=True)

    evidence_id: str
    source_org: str = Field(..., description="Planalto, Receita Federal, CONFAZ, SEFAZ")
    legal_act: str = Field(..., description="Lei, Decreto, Convênio, Instrução Normativa")
    act_number: str
    article: Optional[str] = None
    url: Optional[str] = None
    acquisition_date: date
    content_hash: str


class FiscalRuleCatalogItem(BaseModel):
    model_config = ConfigDict(frozen=True)

    rule_id: str
    version: str = Field(default="1.0")
    valid_from: date
    valid_until: Optional[date] = None
    jurisdiction: Jurisdiction
    tax_type: TaxType
    state: Optional[str] = None
    municipality: Optional[str] = None
    ncm_pattern: Optional[str] = None
    cest: Optional[str] = None
    rate: Decimal
    base_reduction: Decimal = Field(default=Decimal("0.00"))
    mva_rate: Optional[Decimal] = None
    priority: int = Field(default=10)
    evidence: FiscalRuleEvidence
    content_hash: str

    def to_domain_tax_rule(self) -> FiscalTaxRule:
        return FiscalTaxRule(
            rule_id=self.rule_id,
            tax_type=self.tax_type,
            jurisdiction=self.jurisdiction,
            state=self.state,
            municipality=self.municipality,
            effective_from=self.valid_from,
            effective_until=self.valid_until,
            ncm_pattern=self.ncm_pattern,
            priority=self.priority,
            rate=self.rate,
            base_reduction=self.base_reduction,
            mva_rate=self.mva_rate,
            source_legal_node_id=self.evidence.legal_act,
            source_legal_version_id=self.version,
            evidence_id=self.evidence.evidence_id
        )


class FiscalRuleCatalog:
    """
    Catálogo oficial versionado de regras fiscais brasileiras.
    """

    def __init__(self, rules: Optional[List[FiscalRuleCatalogItem]] = None):
        self._rules: List[FiscalRuleCatalogItem] = rules or []

    def register_rule(self, item: FiscalRuleCatalogItem) -> None:
        self._rules.append(item)

    def find_active_rules(self, reference_date: date, tax_type: Optional[TaxType] = None, state: Optional[str] = None) -> List[FiscalTaxRule]:
        active: List[FiscalTaxRule] = []
        for r in self._rules:
            if r.valid_from <= reference_date and (r.valid_until is None or reference_date <= r.valid_until):
                if tax_type and r.tax_type != tax_type:
                    continue
                if state and r.state and r.state != state:
                    continue
                active.append(r.to_domain_tax_rule())
        return active
