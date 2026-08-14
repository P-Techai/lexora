# LÉXORA — RELATÓRIO DE HANDOFF DA FASE 9

**Data:** 2026-08-14  
**Versão Atual:** `v1.2.0-operational-tax-workbench`  
**Migration HEAD:** `0013_operational_tax_workbench`  

---

## 1. Resumo Executivo
A **FASE 9 — OPERATIONAL TAX WORKBENCH & REAL NF-e USER FLOW** foi implementada e concluída com sucesso.

### Destaques da Entrega:
- **Perfis Fiscais de Empresas (`CompanyFiscalProfile`):** Persistência de perfis cadastrais e validação temporal de vigência.
- **Operational Tax Workbench (`OperationalTaxWorkbenchPipeline`):** Transições formais de estado para NF-e (`PROCESSED`, `HUMAN_REVIEW`, `VALIDATION_FAILED`), Produto (`CLASSIFIED`, `HUMAN_REVIEW`) e Decisão (`CONFIRMED`, `HUMAN_REVIEW`).
- **Suíte de Endpoints Workbench:**
  - `POST /api/v1/fiscal/company/profile` & `GET /api/v1/fiscal/company/profile/{company_id}`
  - `POST /api/v1/fiscal/workbench/nfe/upload` & `POST /api/v1/fiscal/workbench/nfe/process`
  - `GET /api/v1/fiscal/workbench/nfe/{nfe_id}` (e suas sub-rotas `/items`, `/classifications`, `/calculations`, `/memory`, `/evidence`, `/report`)
  - `GET /api/v1/fiscal/workbench/reviews/pending` & `POST /api/v1/fiscal/workbench/reviews/{review_id}/action`
- **Migration Alembic `0013_operational_tax_workbench`:** Tabelas `fiscal_company_profiles`, `fiscal_workbench_nfe_documents`, `fiscal_workbench_items` com `ON DELETE RESTRICT`.
- **Suíte de Testes:** 16 testes unitários, cenários Golden e testes PostgreSQL 100% aprovados.

---

## 2. Comandos Principais
- Iniciar API e Dashboard Web UI: `uvicorn src.interfaces.api.main:app --reload`
- Executar Alembic Migrations: `alembic upgrade head`
- Executar Suíte Completa de Testes: `pytest`
