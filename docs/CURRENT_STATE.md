# LÉXORA — Estado Atual do Projeto

**Data da Última Atualização:** 2026-08-14  
**Fase Atual:** FASE 6.3 — COMPLETE (Fiscal Brain & Decision Engine — Two-Brain Governance)  
**Versão Atual:** `v0.10.0-fiscal-brain-foundation`  
**Status da Fase 6.3:** **`FASE 6.3 = COMPLETE`**  
**Status da Fase 6.4:** **`FASE 6.4 = AUTHORIZED`**  
**Status do Projeto:** PROMPT 11 — PASS. Implementação Real do Fiscal Brain e Decision Engine sob governança Two-Brain: 1) Entidades e serviços de domínio determinísticos (`FiscalFact`, `FiscalProductProfile`, `FiscalTaxRule`, `TaxCalculation`, `Decision`, `DecisionTrace`); 2) Zero LLM em decisões tributárias (100% cálculo determinístico Decimal `TaxRoundingService`); 3) Avaliação temporal estrita contra `fact.operation_date` com `TemporalIntegrityValidator.is_date_in_range()`; 4) Parser seguro de NFe XML (`SecureNFeParser`) com proteção XXE e idempotência SHA-256; 5) Migration Alembic `0008_fiscal_brain` com restrição `ON DELETE RESTRICT`; 6) Endpoints `/api/v1/fiscal/classify`, `/api/v1/fiscal/calculate`, `/api/v1/fiscal/decide`, `/api/v1/nfe/import`; 7) Suíte de 40 testes unitários em `tests/unit/test_fiscal_brain.py` e testes PostgreSQL em `tests/integration/test_postgres_fiscal.py`; 8) Documentação e ADR-0017 centralizados.

---

# 1. Resumo do Progresso Recente

- **Fiscal Brain & Decision Engine (v0.10.0-fiscal-brain-foundation):**
  - Implementação da arquitetura Two-Brain: Legal Brain (autoridade normativa) + Fiscal Brain (aplicador de regras formais) + Decision Engine (orquestrador determinístico).
  - Cálculo tributário com precisão Decimal estrita (`TaxRoundingService`) suportando ICMS, ICMS_ST, IPI, PIS, COFINS, ISS, CBS, IBS, IS.
  - Avaliação de regras tributárias pela data de operação (`operation_date`), sem uso de `datetime.now()` ou `date.today()`.
  - Ingestão segura de XMLs de NFe com verificação de idempotência SHA-256 e proteção contra ataques XXE e Billion Laughs.
  - Tabela de decisão com histórico imutável e rastreabilidade total (Fato -> Regra -> Cálculo -> Lei -> Artigo -> Evidência).
  - Suíte completa de 40 cenários de testes unitários em `tests/unit/test_fiscal_brain.py`.
- **Documentação & Relatórios:**
  - `docs/FISCAL_BRAIN.md`, `docs/DECISION_ENGINE.md`, `docs/TWO_BRAINS_ARCHITECTURE.md`, `docs/NFE_PARSING.md`, `docs/adr/ADR-0017-fiscal-brain-decision-engine.md`.

---

# 2. Próxima Tarefa Prioritária

**FASE 6.4 — FISCAL CO-PILOT & AUDIT DASHBOARD (AUTORIZADA)**
1. Interface e assistente interativo para auditoria visual da memória de cálculo e rastreabilidade dos 2 Cérebros;
2. Dashboard de divergências tributárias e alertas de revisão humana (`REVIEW_REQUIRED`, `CONFLICT`);
3. Integração de relatórios executivos auditáveis.
