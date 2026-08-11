from datetime import date
from decimal import Decimal
import pytest

from src.domain.entities.legal_node import LegalNode
from src.domain.entities.tax_calculation import TaxCalculation, TaxItemResult, TaxMemoryLog
from src.domain.enums import LegalNodeType, NodeStatus, TaxRegime, TaxType


def test_legal_node_temporal_validity():
    node = LegalNode(
        id="node-art-3",
        norma_id="lc-87-1996",
        node_type=LegalNodeType.ARTIGO,
        number="Art. 3º",
        text="O imposto não incide sobre operações que destinem ao exterior mercadorias...",
        path="/lc-87-1996/artigo-3",
        position=3,
        metadata={"jurisdiction": "FEDERAL"},
        effective_from=date(1996, 9, 16),
        effective_until=date(2025, 12, 31),
        version=1,
        status=NodeStatus.ACTIVE,
        content_hash="abc123hash"
    )

    # Válido dentro da vigência
    assert node.is_effective_on(date(2020, 5, 10)) is True
    assert node.is_effective_on(date(1996, 9, 16)) is True
    assert node.is_effective_on(date(2025, 12, 31)) is True

    # Inválido fora da vigência
    assert node.is_effective_on(date(1995, 1, 1)) is False
    assert node.is_effective_on(date(2026, 1, 1)) is False


def test_tax_calculation_memory_log_immutability():
    memory_log = TaxMemoryLog(
        id="log-001",
        operation_date=date(2026, 8, 10),
        company_regime=TaxRegime.LUCRO_REAL,
        ncm="84713012",
        cfop="5102",
        cst="000",
        input_values={"product_value": "1000.00"},
        applied_formulas={"icms_value": "base * aliquot"},
        calculated_taxes={"icms": {"value": "180.00"}},
        legal_grounds=["RICMS-SP, Art. 52"],
        engine_version="1.0.0",
        calculation_hash="hash-det-123"
    )

    tax_item = TaxItemResult(
        tax_type=TaxType.ICMS,
        base_value=Decimal("1000.00"),
        aliquot=Decimal("18.00"),
        tax_amount=Decimal("180.00"),
        legal_ground="RICMS-SP, Art. 52"
    )

    calc = TaxCalculation(
        id="calc-001",
        operation_date=date(2026, 8, 10),
        gross_value=Decimal("1000.00"),
        taxes=[tax_item],
        total_tax_amount=Decimal("180.00"),
        memory_log=memory_log
    )

    assert calc.gross_value == Decimal("1000.00")
    assert calc.total_tax_amount == Decimal("180.00")
    assert calc.memory_log.calculation_hash == "hash-det-123"

    # Confirma que os modelos Pydantic congelados (frozen) imutáveis rejeitam alterações diretas
    with pytest.raises(Exception):
        calc.gross_value = Decimal("2000.00")
