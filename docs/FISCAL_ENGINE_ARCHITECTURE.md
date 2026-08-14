# LÉXORA — Arquitetura do Motor Fiscal Operacional (Fiscal Engine Architecture)

Este documento detalha a arquitetura do motor fiscal determinístico do **LÉXORA (LXR)** na **FASE 7**.

---

# 1. Arquitetura de Camadas

1. **Pipeline de Análise (`NFeAnalysisPipeline`):** Ponto central de entrada para cargas úteis XML de NF-e.
2. **Camada de Parse & Segurança (`SecureNFeParser`):** Sanitização, bloqueio de XXE, limites de tamanho e validação de encoding.
3. **Resolução Determinística de Regras (`TaxRuleResolver`):** Seleção de regras ativas com base estrita na data de operação (`operation_date`).
4. **Motor de Cálculo Financeiro (`TaxCalculationEngine`):** Operação 100% sobre `Decimal` (`ROUND_HALF_UP`) para todos os tributos estaduais, federais e municipais.
5. **Memória de Cálculo Reconstruível (`CalculationMemory`):** Snapshot dos inputs e fórmulas com hash SHA-256 (`memory_hash`).
6. **Assistência Explicativa (`FiscalCopilotService`):** O LLM atua estritamente como camada linguística explicativa (`LLM = EXPLANATION ONLY`).
