# ADR-0022: Operational Tax Workbench e Fluxo de Usuário NF-e

- **Status:** Aceito
- **Data:** 2026-08-14
- **Autores:** Equipe de Arquitetura LÉXORA

---

## 1. Contexto e Problema

Com a conclusão da ingestão de conhecimento fiscal oficial e a infraestrutura de lote na FASE 8, fez-se necessária a estruturação da camada de Workbench Operacional de Usuário para gerenciar perfis fiscais de empresas, upload, validação de schema XML, classificação de produto, cálculo determinístico, fila de revisão humana e geração de relatórios.

---

## 2. Decisão

1. **Persistência de Perfil Fiscal de Empresa (`CompanyFiscalProfile`):** Tabela `fiscal_company_profiles` com validação temporal estrita contra `reference_date`.
2. **Máquina de Estados de NF-e, Produto e Decisão:** Estados explícitos (`PROCESSED`, `HUMAN_REVIEW`, `VALIDATION_FAILED`, `CLASSIFIED`, `CONFIRMED`).
3. **Multi-Tenancy e Isolamento Incondicional:** Isolamento por `company_id` nas camadas de aplicação e banco de dados.
4. **Migration `0013_operational_tax_workbench`:** Tabelas `fiscal_company_profiles`, `fiscal_workbench_nfe_documents`, `fiscal_workbench_items` com `ON DELETE RESTRICT`.
