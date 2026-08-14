# LÉXORA — CHANGELOG DE VERSÕES

## [v0.11.0-fiscal-copilot] — 2026-08-14
### Adicionado
- **Fiscal Co-Pilot Assistant (`FiscalCopilotService`):** Explicação determinística de decisões tributárias e memória de cálculo (`LLM = EXPLANATION ONLY`).
- **Audit Dashboard Web UI (`GET /dashboard`):** Interface web portável e moderna servida pelo FastAPI.
- **Workflow de Revisão Humana (`ReviewStateMachine`):** Transições estritas (`OPEN` -> `IN_REVIEW` -> `APPROVED` / `REJECTED` / `ESCALATED`).
- **Audit Log Append-Only (`ReviewEvent` & `HumanOverride`):** Assinaturas SHA-256 e preservação da decisão original intacta.
- **Fiscal Diff Engine (`FiscalDiffEngine`):** Comparação lado a lado entre decisões históricas e reprocessadas.
- **Migration Alembic `0009_fiscal_copilot_audit`:** Tabelas `fiscal_reviews`, `fiscal_review_events`, `fiscal_human_overrides`.
- **Suíte de Testes:** Unitários, Golden Scenarios `GOLDEN-REVIEW-001..004` e testes PostgreSQL.

## [v0.10.0-fiscal-brain-foundation] — 2026-08-14
### Adicionado
- **Fiscal Brain & Decision Engine (FASE 6.3):** Classificação determinística, cálculos Decimal `ROUND_HALF_UP` e governança Two-Brain.

## [v0.9.1-contextual-rag-production-lock] — 2026-08-14
### Adicionado
- Selagem de Produção da Fase 6.2 com geradores via `LegalAnswerGeneratorFactory`.
