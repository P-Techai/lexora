# LÉXORA — CHANGELOG DE VERSÕES

## [v0.12.0-fiscal-classification-tax-engine] — 2026-08-14
### Adicionado
- **Perfis Fiscais Cadastrais de Produtos (`FiscalProductProfile`):** Suporte a GTIN, NCM, CEST, unidade, origem e status determinístico de classificação.
- **Memórias de Cálculo Auditáveis (`CalculationMemory`):** Reconstrução explícita de inputs e fórmulas para ICMS, ICMS-ST, IPI, PIS, COFINS, ISS, FCP, FCP-ST em precisão `Decimal` (`ROUND_HALF_UP`).
- **Resolvedor de Regras por Data de Operação (`TaxRuleResolver`):** Aplicação estrita da temporalidade em `operation_date`.
- **Reprocessamento Não-Destrutivo (`ReprocessingService`):** Preservação integral de decisões históricas passadas.
- **Migration Alembic `0010_fiscal_classification_tax_engine`:** Tabelas `fiscal_product_profiles`, `fiscal_calculation_memories`, `fiscal_document_results`, `fiscal_reprocessing_runs`.
- **Suíte de Testes:** 26 testes unitários, Golden Scenarios 1, 2, 3 e testes de integração PostgreSQL.

## [v0.11.0-fiscal-copilot] — 2026-08-14
### Adicionado
- **Fiscal Co-Pilot Assistant & Audit Dashboard Web UI (FASE 6.4):** Interface web portável, assistente explicativo (`LLM = EXPLANATION ONLY`), workflow de revisão humana e audit trail append-only.

## [v0.10.0-fiscal-brain-foundation] — 2026-08-14
### Adicionado
- **Fiscal Brain & Decision Engine (FASE 6.3):** Classificação determinística, cálculos Decimal `ROUND_HALF_UP` e governança Two-Brain.

## [v0.9.1-contextual-rag-production-lock] — 2026-08-14
### Adicionado
- Selagem de Produção da Fase 6.2 com geradores via `LegalAnswerGeneratorFactory`.
