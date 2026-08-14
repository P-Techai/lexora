import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import TaxType


class CalculationMemory(BaseModel):
    """
    Memória de cálculo auditável e reconstruível para uma apuração tributária de item.
    """
    model_config = ConfigDict(frozen=True)

    calculation_id: str = Field(..., description="ID único do cálculo")
    operation_id: str = Field(..., description="ID da operação fiscal")
    item_id: str = Field(..., description="ID do item da operação")
    tax_type: TaxType = Field(..., description="Tipo de tributo (ICMS, ICMS_ST, IPI, PIS, COFINS, ISS, FCP, FCP_ST)")
    taxable_base: Decimal = Field(..., description="Base de cálculo apurada em Decimal")
    rate: Decimal = Field(..., description="Alíquota aplicada em Decimal")
    calculated_amount: Decimal = Field(..., description="Valor apurado em Decimal")
    inputs: Dict[str, Any] = Field(..., description="Snapshot dos inputs monetários e quantitativos utilizados")
    formula: str = Field(..., description="Fórmula explícita reconstruível (ex: base = qty * unit - desc; amount = base * rate)")
    rounding_policy: str = Field(default="ROUND_HALF_UP", description="Política de arredondamento utilizada")
    rule_id: Optional[str] = Field(None, description="ID da regra fiscal aplicada")
    legal_reference: Optional[str] = Field(None, description="Fundamento legal normativo vinculado")
    evidence_id: Optional[str] = Field(None, description="ID da evidência jurídica auditada")
    calculated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    memory_hash: str = Field(..., description="Hash SHA-256 garantindo a integridade dos valores do cálculo")

    @classmethod
    def create(
        cls,
        calculation_id: str,
        operation_id: str,
        item_id: str,
        tax_type: TaxType,
        taxable_base: Decimal,
        rate: Decimal,
        calculated_amount: Decimal,
        inputs: Dict[str, Any],
        formula: str,
        rule_id: Optional[str] = None,
        legal_reference: Optional[str] = None,
        evidence_id: Optional[str] = None
    ) -> "CalculationMemory":
        raw_data = f"{calculation_id}|{operation_id}|{item_id}|{tax_type.value}|{taxable_base}|{rate}|{calculated_amount}|{json.dumps(inputs, sort_keys=True)}|{rule_id}"
        hash_val = hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

        return cls(
            calculation_id=calculation_id,
            operation_id=operation_id,
            item_id=item_id,
            tax_type=tax_type,
            taxable_base=taxable_base,
            rate=rate,
            calculated_amount=calculated_amount,
            inputs=inputs,
            formula=formula,
            rounding_policy="ROUND_HALF_UP",
            rule_id=rule_id,
            legal_reference=legal_reference,
            evidence_id=evidence_id,
            memory_hash=hash_val
        )
