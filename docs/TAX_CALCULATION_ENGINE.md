# LÉXORA — Motor de Apuração e Cálculo Tributário (Tax Calculation Engine)

Este documento especifica o motor determinístico de apuração de tributos do **LÉXORA (LXR)** na **FASE 6.5**.

---

# 1. Arquitetura do Motor de Apuração

```text
FiscalFact / Item
   ↓
TaxRuleResolver (Consulta regras ativas na data da operação)
   ↓
TaxBaseCalculator (Apura base de cálculo e reduções Decimal)
   ↓
TaxRateResolver (Aplica alíquotas com base na UF/Jurisdição)
   ↓
TaxAmountCalculator (Aplica ROUND_HALF_UP Decimal)
   ↓
TaxCalculationMemoryBuilder (Gera memória auditável com hash SHA-256)
```

---

# 2. Tributos Suportados

- **Estaduais:** ICMS, ICMS-ST, DIFAL, FCP, FCP-ST.
- **Federais:** IPI, PIS, COFINS, CBS, IBS, IS.
- **Municipais:** ISS.

---

# 3. Matemática Financeira Estrita

Toda a apuração opera exclusivamente sobre a classe `Decimal` em escala de 2 casas para valores e 4 casas para alíquotas. O uso de `float` é estritamente proibido.
