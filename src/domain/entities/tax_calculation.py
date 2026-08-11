from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict

from src.domain.enums import TaxRegime, TaxType


class TaxItemResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    tax_type: TaxType
    base_value: Decimal
    aliquot: Decimal
    tax_amount: Decimal
    legal_ground: str


class TaxMemoryLog(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    operation_date: date
    company_regime: TaxRegime
    ncm: str
    cfop: str
    cst: str
    input_values: Dict[str, str]
    applied_formulas: Dict[str, str]
    calculated_taxes: Dict[str, Dict[str, str]]
    legal_grounds: List[str]
    engine_version: str = "1.0.0"
    calculation_hash: str


class TaxCalculation(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    operation_date: date
    gross_value: Decimal
    taxes: List[TaxItemResult]
    total_tax_amount: Decimal
    memory_log: TaxMemoryLog
