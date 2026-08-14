# LÉXORA — ROADMAP OFICIAL DA PLATAFORMA

---

## Fases do Projeto LÉXORA (LXR)

### Fundação Jurídica e RAG (Fases 1–6.2) — CLOSED / SEALED
- **Fase 1 a 5:** Modelo Canônico Jurídico, Aquisição, Versionamento, Validação Temporal e Notações Normativas.
- **Fase 6.1 (Hybrid Legal Retrieval):** Busca vetorial e FTS híbrida PostgreSQL (`v0.8.0-retrieval-foundation`).
- **Fase 6.2 (Contextual Legal RAG):** RAG Contextual, Answer Guardrails e Citação de Proveniência (`v0.9.1-contextual-rag-production-lock`).

---

### Motor Fiscal & Governança Two-Brain (Fases 6.3–6.4) — COMPLETE

- **Fase 6.3 (Fiscal Brain & Decision Engine):** `COMPLETE` (`v0.10.0-fiscal-brain-foundation`)
  - Classificação determinística, cálculos `Decimal` `ROUND_HALF_UP` (ICMS, ICMS-ST, IPI, PIS, COFINS, ISS, CBS, IBS, IS).
  - Parser seguro de NFe XML (`SecureNFeParser`) e migration `0008_fiscal_brain`.

- **Fase 6.4 (Fiscal Co-Pilot & Audit Dashboard):** `COMPLETE` (`v0.11.0-fiscal-copilot`)
  - Interface Web Dashboard (`/dashboard`), assistente explicativo (`LLM = EXPLANATION ONLY`).
  - Workflow de revisão humana com máquina de estados, eventos imutáveis (`ReviewEvent`), `HumanOverride` e `FiscalDiffEngine`.
  - Migration Alembic `0009_fiscal_copilot_audit` e relatórios auditáveis.

---

### Próxima Fase (Fase 6.5 / Fase 7) — AUTHORIZED UNDER DEMAND
- Módulos avançados de integração e expansão nacional sob solicitação explícita.
