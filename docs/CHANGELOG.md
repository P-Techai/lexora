# LÉXORA — CHANGELOG DE VERSÕES

## [v1.2.0-operational-tax-workbench] — 2026-08-14
### Adicionado
- **Operational Tax Workbench & Real NF-e User Flow (FASE 9):** Implementação completa do fluxo operacional de usuário `COMPANY -> PROFILE -> XML -> VALIDATION -> CLASSIFICATION -> RULE -> CALCULATION -> HUMAN REVIEW -> DECISION -> TRACE -> REPORT`.
- **Perfis Fiscais de Empresas (`CompanyFiscalProfile`):** Persistência relacional e validação temporal estrita de vigência.
- **Transições Formais de Ciclo de Vida:** Estados explícitos para NF-e, Produtos e Decisões.
- **Endpoints de Workbench:** Ingestão, consulta de itens, memórias de cálculo, evidências e relatórios.
- **Migration Alembic `0013_operational_tax_workbench`:** Tabelas `fiscal_company_profiles`, `fiscal_workbench_nfe_documents`, `fiscal_workbench_items`.

## [v1.1.0-real-fiscal-knowledge-batch-nfe] — 2026-08-14
### Adicionado
- **Catálogo Oficial Versionado de Regras Fiscais (`FiscalRuleCatalog`):** Regras brasileiras com hash imutável e evidências legais oficiais.
- **Serviço de Classificação de Produtos (`ProductFiscalClassificationService`):** Definição determinística de NCM, CEST, CST, CSOSN e CFOP.
- **Processamento em Lote de NF-e (`NFeBatchPipeline`):** Ingestão resiliente via `POST /api/v1/fiscal/nfe/batch`.

## [v1.0.0-operational-fiscal-engine] — 2026-08-14
### Adicionado
- **Pipeline Operacional NF-e End-to-End (`NFeAnalysisPipeline`):** Ingestão e análise determinística de XML de NF-e via `POST /api/v1/fiscal/nfe/analyze`.
