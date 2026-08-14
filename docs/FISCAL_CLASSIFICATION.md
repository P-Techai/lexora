# LÉXORA — Classificação Fiscal Determinística de Produtos (Fiscal Classification)

Este documento especifica a classificação determinística de produtos, NCM, CEST, CST, CSOSN e CFOP do **LÉXORA (LXR)** na **FASE 6.5**.

---

# 1. Princípio Fundamental de Não-Inferência Libertária

- **Proibição de Guessing:** O LÉXORA NUNCA infere ou inventa NCM, CEST, CST ou CFOP por mera similaridade textual sem fundamentação em regra legal ou documento oficial.
- **Status de Classificação:**
  - `CLASSIFIED`: Evidência suficiente e regra fiscal determinada.
  - `PARTIALLY_CLASSIFIED`: Atributos parciais determinados.
  - `REVIEW_REQUIRED`: Exige intervenção humana por NCM/CST inválido ou ausente.
  - `CONFLICT`: Evidências ou regras incompatíveis.
  - `UNCLASSIFIED`: Informação insuficiente.

---

# 2. Resolução de Códigos Fiscais

1. **NCM:** Validação estrutural de 8 dígitos numéricos. Erros geram `NCM_INVALID` / `REVIEW_REQUIRED`.
2. **CEST:** Vinculado obrigatoriamente a regras de Substituição Tributária.
3. **CST / CSOSN:** Apurado em função da empresa, regime tributário (Lucro Real, Presumido, Simples), UF e operação.
4. **CFOP:** Apurado considerando origem/destino UF, finalidade (comercialização, industrialização, uso/consumo), tipo de consumidor e operação.
