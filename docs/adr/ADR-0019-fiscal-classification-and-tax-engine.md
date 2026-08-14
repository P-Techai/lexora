# ADR-0019: Classificação Fiscal de Produtos e Motor de Apuração Tributária

- **Status:** Aceito
- **Data:** 2026-08-14
- **Autores:** Equipe de Arquitetura LÉXORA

---

## 1. Contexto e Problema

Com a superfície operacional e o assistente Co-Pilot sintonizados na FASE 6.4, fez-se necessária a expansão do motor determinístico para tratar perfis cadastrais de produtos, validação estrutural de NCM/CEST, resolução de CST/CFOP por contexto e geração de memórias de cálculo auditáveis para tributos estaduais, federais e municipais.

---

## 2. Decisão

1. **Proibição de Guessing:** O sistema NUNCA infere NCM ou alíquotas por aproximação probabilística de I.A. Inconsistências disparam `REVIEW_REQUIRED` ou `CONFLICT`.
2. **Autoridade Temporal da Data de Operação:** As regras tributárias aplicáveis são resolvidas estritamente com base na data da operação (`operation_date`), garantindo a imutabilidade do passado tributário.
3. **Memória de Cálculo Reconstruível (`CalculationMemory`):** Todo cálculo tributário armazena um snapshot dos inputs monetários e a fórmula explícita em precisão `Decimal` (`ROUND_HALF_UP`) com hash SHA-256.
4. **Reprocessamento Não-Destrutivo:** Novas execuções mantêm as decisões anteriores intactas através do modelo `FiscalReprocessingRun`.

---

## 3. Consequências

- Rastreabilidade e reprodutibilidade 100% garantidas para auditorias fiscais e tributárias.
- Proteção total da integridade relacional com chave estrangeira `ON DELETE RESTRICT`.
