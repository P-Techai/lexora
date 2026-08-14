# LÉXORA — Memória de Cálculo Auditável (`CalculationMemory`)

Este documento especifica a memória de cálculo tributário do **LÉXORA (LXR)** na **FASE 6.5**.

---

# 1. Estrutura da Memória de Cálculo (`CalculationMemory`)

Toda apuração individual gera um registro imutável no PostgreSQL (`fiscal_calculation_memories`) contendo:
- `calculation_id`: ID único do cálculo.
- `operation_id`: ID da operação fiscal.
- `item_id`: ID do item.
- `tax_type`: Tipo do tributo.
- `taxable_base`: Base de cálculo apurada (Decimal).
- `rate`: Alíquota aplicada (Decimal).
- `calculated_amount`: Valor do imposto apurado (Decimal).
- `inputs`: Snapshot dos valores monetários e quantitativos utilizados.
- `formula`: Fórmula explícita em texto reconstruível.
- `rounding_policy`: Política `ROUND_HALF_UP`.
- `rule_id`: Regra aplicada.
- `legal_reference`: Dispositivo normativo vinculado.
- `evidence_id`: Evidência jurídica vinculada.
- `memory_hash`: Assinatura determinística SHA-256 dos componentes do cálculo.
