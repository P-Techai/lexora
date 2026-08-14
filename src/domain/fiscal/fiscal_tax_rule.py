from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import Jurisdiction, TaxType


class FiscalTaxRule(BaseModel):
    """
    Entidade de Regra Fiscal Tributária formalizada.
    Exige obrigatoriamente vinculação à fundamentação legal (source_legal_node_id, source_legal_version_id, evidence_id)
    para ser considerada uma regra CONFIRMED.
    """
    model_config = ConfigDict(frozen=True)

    rule_id: str = Field(..., description="Identificador único da regra fiscal")
    tax_type: TaxType = Field(..., description="Tipo do tributo (ICMS, IPI, PIS, COFINS, ISS, etc.)")
    jurisdiction: Jurisdiction = Field(..., description="Jurisdição (FEDERAL, STATE, MUNICIPAL)")
    state: Optional[str] = Field(None, description="UF aplicável se estadual")
    municipality: Optional[str] = Field(None, description="Município aplicável se municipal")
    effective_from: date = Field(..., description="Início do período de vigência [effective_from, effective_until)")
    effective_until: Optional[date] = Field(None, description="Fim do período de vigência se houver")
    priority: int = Field(default=100, description="Prioridade de aplicação determinística (menor número = maior prioridade)")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Condições de correspondência da regra")
    formula: str = Field(default="base * rate", description="Fórmula textual auditável do cálculo")
    rate: Decimal = Field(default=Decimal("0.00"), description="Alíquota tributária em percentual Decimal (ex: 18.00 = 18%)")
    base_reduction: Decimal = Field(default=Decimal("0.00"), description="Percentual de redução de base em Decimal (ex: 33.33)")
    is_exempt: bool = Field(default=False, description="Indica se há isenção fiscal")
    has_benefit: bool = Field(default=False, description="Indica se há benefício fiscal específico")
    source_legal_node_id: Optional[str] = Field(None, description="ID do nó normativo legal de origem")
    source_legal_version_id: Optional[str] = Field(None, description="ID da versão legal de origem")
    evidence_id: Optional[str] = Field(None, description="ID da evidência jurídica auditada")
    rule_version: int = Field(default=1, description="Versão da regra fiscal")
    status: str = Field(default="ACTIVE", description="Status da regra (ACTIVE, SUPERSEDED, REVOKED)")
