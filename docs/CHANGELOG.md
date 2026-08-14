# LÉXORA — CHANGELOG DE VERSÕES

## [v1.0.0-operational-fiscal-engine] — 2026-08-14
### Adicionado
- **Pipeline Operacional NF-e End-to-End (`NFeAnalysisPipeline`):** Ingestão e análise determinística de XML de NF-e via `POST /api/v1/fiscal/nfe/analyze`.
- **Defesa Contra XXE e Limite de Payload:** Sanitização rigorosa no `SecureNFeParser` (máx. 10MB).
- **Preservação de Fatos Originais vs Decisão:** Armazenamento dos impostos, CST e CFOP originais como `SOURCE FACT` e apuração como `SYSTEM DECISION`.
- **Cinco Cenários Golden:** Operação interna, interestadual, temporalidade 2024 vs 2025, ambiguidade e conflitos normativos.
- **Migration Alembic `0011_nfe_operational_fiscal_engine`:** Tabela `fiscal_nfe_analyses` com `ON DELETE RESTRICT`.

## [v0.12.0-fiscal-classification-tax-engine] — 2026-08-14
### Adicionado
- **Perfis Fiscais Cadastrais de Produtos (`FiscalProductProfile`):** Suporte a GTIN, NCM, CEST, unidade, origem e status determinístico de classificação.
- **Memórias de Cálculo Auditáveis (`CalculationMemory`):** Reconstrução explícita de inputs e fórmulas para ICMS, ICMS-ST, IPI, PIS, COFINS, ISS, FCP, FCP-ST em precisão `Decimal` (`ROUND_HALF_UP`).

## [v0.11.0-fiscal-copilot] — 2026-08-14
### Adicionado
- **Fiscal Co-Pilot Assistant & Audit Dashboard Web UI (FASE 6.4):** Interface web portável, assistente explicativo (`LLM = EXPLANATION ONLY`), workflow de revisão humana e audit trail append-only.
