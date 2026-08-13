# LÉXORA — Handoff do Projeto

Este documento orienta novos agentes de IA e desenvolvedores sobre como assumir o projeto **LÉXORA (LXR)** sem perda de contexto ou violação da Constituição.

---

# 1. Status do Projeto

- **Fase Atual:** FASE 6.2 — SEALED (Selamento de Produção do RAG Jurídico Contextual)
- **Versão Atual:** `v0.9.1-contextual-rag-production-lock`
- **Status da Fase 6.2:** **`FASE 6.2 = SEALED`**
- **Status da Fase 6.3:** **`FASE 6.3 = AUTHORIZED`** (Pronta para Início Imediato)

---

# 2. Instruções para Início de Turno (Start Protocol)

Siga o checklist do [.agents/workflows/start_session.md](.agents/workflows/start_session.md) e leia na seguinte ordem:

1. [README.md](README.md)
2. [docs/PROJECT.md](docs/PROJECT.md)
3. [docs/PROJECT_MEMORY.md](docs/PROJECT_MEMORY.md)
4. [docs/AGENT_PROTOCOL.md](docs/AGENT_PROTOCOL.md)
5. [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md)
6. [docs/HANDOFF.md](docs/HANDOFF.md)
7. [docs/PHASE6_2_PRODUCTION_LOCK.md](docs/PHASE6_2_PRODUCTION_LOCK.md)
8. [docs/LEGAL_RAG_ARCHITECTURE.md](docs/LEGAL_RAG_ARCHITECTURE.md)
9. [docs/LEGAL_ANSWER_GUARDRAILS.md](docs/LEGAL_ANSWER_GUARDRAILS.md)
10. [docs/DECISIONS.md](docs/DECISIONS.md) e arquivos em [docs/adr/](docs/adr/)
11. Regras em [.agents/rules/](.agents/rules/)
12. Código em `src/` e testes em `tests/`.

---

# 3. Checklist de Finalização de Tarefa (End Protocol)

- [ ] Executar testes unitários e de integração (`pytest`);
- [ ] Atualizar `docs/CHANGELOG.md`;
- [ ] Atualizar `docs/CURRENT_STATE.md`;
- [ ] Atualizar `docs/HANDOFF.md` com o próximo passo prioritário;
- [ ] Criar novo ADR em `docs/adr/` se uma decisão arquitetural foi tomada;
- [ ] Apresentar o Relatório Final com os itens obrigatórios da entrega.

---

# 4. Próxima Tarefa Prioritária

**Próxima Fase:** FASE 6.3 — FISCAL BRAIN & DECISION ENGINE (**AUTORIZADA**)  
**Versão Atual:** `v0.9.1-contextual-rag-production-lock`  
**Tarefa Imediata:** 
1. Iniciar o desenvolvimento da FASE 6.3;
2. Projetar a arquitetura do Fiscal Brain para classificação e regras tributárias (ICMS, PIS/COFINS, ISS, IBS/CBS/IS);
3. Garantir que 100% dos pareceres do Fiscal Brain mantenham citações de evidência normativas auditáveis provindas da camada selada da Fase 6.2.
