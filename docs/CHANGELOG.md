# LÉXORA — CHANGELOG DE VERSÕES

## [v1.1.0-real-fiscal-knowledge-batch-nfe] — 2026-08-14
### Adicionado
- **Catálogo Oficial Versionado de Regras Fiscais (`FiscalRuleCatalog`):** Regras brasileiras com hash imutável e evidências legais oficiais.
- **Serviço de Classificação de Produtos (`ProductFiscalClassificationService`):** Definição determinística de NCM, CEST, CST, CSOSN e CFOP.
- **Processamento em Lote de NF-e (`NFeBatchPipeline`):** Ingestão resiliente via `POST /api/v1/fiscal/nfe/batch`.
- **Dez Cenários Golden (`GOLDEN-08.01` a `GOLDEN-08.10`):** Cobertura completa de tributos estaduais, federais e municipais.
- **Migration Alembic `0012_real_fiscal_knowledge_batch_nfe`:** Tabelas `fiscal_rule_catalog`, `fiscal_nfe_batches`, `fiscal_batch_items`.

## [v1.0.0-operational-fiscal-engine] — 2026-08-14
### Adicionado
- **Pipeline Operacional NF-e End-to-End (`NFeAnalysisPipeline`):** Ingestão e análise determinística de XML de NF-e via `POST /api/v1/fiscal/nfe/analyze`.
- **Defesa Contra XXE e Limite de Payload:** Sanitização rigorosa no `SecureNFeParser` (máx. 10MB).
- **Cinco Cenários Golden:** Operação interna, interestadual, temporalidade 2024 vs 2025, ambiguidade e conflitos normativos.

## [v0.12.0-fiscal-classification-tax-engine] — 2026-08-14
### Adicionado
- **Perfis Fiscais Cadastrais de Produtos (`FiscalProductProfile`):** Suporte a GTIN, NCM, CEST, unidade, origem e status determinístico de classificação.
- **Memórias de Cálculo Auditáveis (`CalculationMemory`):** Reconstrução explícita de inputs e fórmulas para ICMS, ICMS-ST, IPI, PIS, COFINS, ISS, FCP, FCP-ST em precisão `Decimal` (`ROUND_HALF_UP`).
