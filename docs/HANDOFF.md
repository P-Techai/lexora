# LÉXORA — Handoff do Projeto

Este documento orienta novos agentes de IA e desenvolvedores sobre como assumir o projeto **LÉXORA (LXR)** sem perda de contexto ou violação da Constituição.

---

# 1. Status do Projeto

- **Fase Atual:** FASE 6.3 — COMPLETE (Fiscal Brain & Decision Engine — Two-Brain Governance)
- **Versão Atual:** `v0.10.0-fiscal-brain-foundation`
- **Status da Fase 6.3:** **`FASE 6.3 = COMPLETE`**
- **Status da Fase 6.4:** **`FASE 6.4 = AUTHORIZED`** (Pronta para Início Imediato)

---

# 2. Instruções para Início de Turno (Start Protocol)

Siga o checklist do [.agents/workflows/start_session.md](.agents/workflows/start_session.md) e leia na seguinte ordem:

1. [README.md](README.md)
2. [docs/PROJECT.md](docs/PROJECT.md)
3. [docs/PROJECT_MEMORY.md](docs/PROJECT_MEMORY.md)
4. [docs/AGENT_PROTOCOL.md](docs/AGENT_PROTOCOL.md)
5. [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md)
6. [docs/HANDOFF.md](docs/HANDOFF.md)
7. [docs/FISCAL_BRAIN.md](docs/FISCAL_BRAIN.md)
8. [docs/DECISION_ENGINE.md](docs/DECISION_ENGINE.md)
9. [docs/TWO_BRAINS_ARCHITECTURE.md](docs/TWO_BRAINS_ARCHITECTURE.md)
10. [docs/NFE_PARSING.md](docs/NFE_PARSING.md)
11. [docs/DECISIONS.md](docs/DECISIONS.md) e arquivos em [docs/adr/](docs/adr/)
12. Regras em [.agents/rules/](.agents/rules/)
13. Código em `src/` e testes em `tests/`.

---

# 3. Checklist de Finalização de Tarefa (End Protocol)

- [ ] Executar testes unitários e de integração (`pytest`);
- [ ] Atualizar `docs/CHANGELOG.md`;
- [ ] Atualizar `docs/CURRENT_STATE.md`;
- [ ] Atualizar `docs/HANDOFF.md` com o próximo passo prioritário;
- [ ] Registrar decisões em `docs/DECISIONS.md` ou novos arquivos ADR em `docs/adr/`;
- [ ] Fazer commit com mensagem semântica no Git.

---

# 4. Próxima Tarefa Prioritária

**FASE 6.4 — FISCAL CO-PILOT & AUDIT DASHBOARD (AUTORIZADA)**
- Implementar interface visual e assistente para auditoria da memória de cálculo e rastreabilidade Two-Brain.
- Dashboard de revisão humana para alertas `REVIEW_REQUIRED` e `CONFLICT`.
