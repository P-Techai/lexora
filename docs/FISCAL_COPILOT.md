# LÉXORA — Especificação do Co-Pilot Fiscal (Fiscal Co-Pilot)

Este documento especifica o assistente de auditoria **Fiscal Co-Pilot** do **LÉXORA (LXR)** implementado na **FASE 6.4**.

---

# 1. Princípio de Explicação Soberana (`LLM = EXPLANATION ONLY`)

O **Fiscal Co-Pilot** atua como uma camada assistencial para explicação humanizada e síntese explicativa sobre o resultado gerado pelo **Decision Engine**.

- **Soberania do Motor:** O Co-Pilot NUNCA altera o resultado do cálculo tributário (`tax_amount`), alíquota (`rate`), base (`taxable_base`), CST, CFOP ou NCM.
- **Fluxo:** `Decision Engine (Autoritativo) -> Context Pack -> FiscalCopilotService -> Explicação Exponível`.

---

# 2. Funcionalidades do Co-Pilot

1. **Explicação de Decisão (`POST /api/v1/fiscal/copilot/explain`):** Retorna resumo textual humanizado, regras aplicadas, regras rejeitadas, cálculos efetuados e links de fundamentação legal.
2. **Síntese de Memória de Cálculo:** Explica passo a passo como o valor tributário foi derivado a partir das entradas Decimal.
3. **Alertas de Inconsistência:** Destaca quando uma revisão humana (`REVIEW_REQUIRED`, `CONFLICT`) se faz necessária.
