# LÉXORA — Modelo de Cálculo e Memória Fiscal (Fiscal Calculation Model)

Este documento especifica a matemática determinística e a memória de cálculo do **LÉXORA (LXR)**.

---

# 1. Matemática Decimal Estrita

Todo cálculo tributário no LÉXORA utiliza a classe `Decimal` do Python. É estritamente proibido o uso de `float` para quantias financeiras ou alíquotas.

- **Serviço de Arredondamento:** `TaxRoundingService`
- **Estratégia:** `ROUND_HALF_UP`
- **Escala de Valores Monetários:** 2 casas decimais (ex.: `R$ 180.00`).
- **Escala de Alíquotas:** 4 casas decimais (ex.: `18.0000%`).

---

# 2. Fórmula de Cálculo

1. **Base de Cálculo:**
   $$\text{taxable\_base} = \text{total\_value} \times \left(1 - \frac{\text{base\_reduction}}{100}\right)$$
2. **Valor do Imposto:**
   $$\text{calculated\_amount} = \text{TaxRoundingService.round\_amount}\left(\text{taxable\_base} \times \frac{\text{rate}}{100}\right)$$

---

# 3. Memória de Cálculo Auditável (`TaxCalculationLog`)

Cada cálculo produz um registro auditável no PostgreSQL (`fiscal_calculation_logs`) contendo `calculation_id`, `input_hash`, `fact_snapshot`, `rule_snapshot`, `formula`, `base`, `rate`, `reduction`, `result`, `rounding`, `legal_basis` e `reference_date`.
