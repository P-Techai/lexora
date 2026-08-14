# LÉXORA — Modelo Canônico de Regra Fiscal (Fiscal Rule Model)

Este documento especifica a estrutura declarativa e o modelo de dados de **Regra Fiscal (FiscalTaxRule)** do **LÉXORA (LXR)**.

---

# 1. Estrutura da Regra Fiscal (`FiscalTaxRule`)

Toda regra tributária no LÉXORA é uma entidade declarativa e imutável contendo:

- `rule_id`: Identificador único da regra fiscal.
- `tax_type`: Tipo do tributo (`ICMS`, `ICMS_ST`, `IPI`, `PIS`, `COFINS`, `ISS`, `CBS`, `IBS`, `IS`).
- `jurisdiction`: Jurisdição (`FEDERAL`, `STATE`, `MUNICIPAL`).
- `state`: Sigla da UF aplicável se estadual.
- `municipality`: Código do município se municipal.
- `effective_from`: Data de início de vigência.
- `effective_until`: Data de término de vigência (opcional se contínua).
- `priority`: Prioridade de aplicação determinística (menor valor = maior prioridade).
- `formula`: Fórmula textual declarativa (ex.: `base * rate`).
- `rate`: Alíquota em percentual Decimal (ex.: `18.00`).
- `base_reduction`: Redução de base de cálculo em percentual Decimal.
- `is_exempt`: Flag booleana indicando isenção fiscal.
- `has_benefit`: Flag booleana indicando benefício fiscal.
- `source_legal_node_id`: Vínculo com o nó legal do **Legal Brain**.
- `source_legal_version_id`: Vínculo com a versão normativa do **Legal Brain**.
- `evidence_id`: Vínculo com a evidência auditada.

---

# 2. Proibição de Regras Órfãs

Regras em status `ACTIVE` sem vínculo com `source_legal_node_id`, `source_legal_version_id` e `evidence_id` disparam o status `LEGAL_BASIS_MISSING` / `REVIEW_REQUIRED` no **Decision Engine**.
