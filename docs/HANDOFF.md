# LÉXORA — Handoff do Projeto

Este documento orienta novos agentes de IA e desenvolvedores sobre como assumir o projeto **LÉXORA (LXR)** sem perda de contexto ou violação da Constituição.

---

# 1. Status do Projeto

- **Fase Atual:** FASE 5 — CLOSED (Fundação Encerrada e Selada)
- **Versão Atual:** `v0.7.3-foundation-closed`
- **Status da Fundação:** **`FOUNDATION = CLOSED`**
- **Status da FASE 6:** **`FASE 6 = AUTHORIZED`** (Pronta para Início Imediato)

---

# 2. Instruções para Início de Turno (Start Protocol)

Siga o checklist do [.agents/workflows/start_session.md](.agents/workflows/start_session.md) e leia na seguinte ordem:

1. [README.md](README.md)
2. [docs/PROJECT.md](docs/PROJECT.md)
3. [docs/PROJECT_MEMORY.md](docs/PROJECT_MEMORY.md)
4. [docs/AGENT_PROTOCOL.md](docs/AGENT_PROTOCOL.md)
5. [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md)
6. [docs/HANDOFF.md](docs/HANDOFF.md)
7. [docs/FINAL_FOUNDATION_LOCK_REPORT.md](docs/FINAL_FOUNDATION_LOCK_REPORT.md)
8. [docs/FINAL_FOUNDATION_LOCK.md](docs/FINAL_FOUNDATION_LOCK.md)
9. [docs/FINAL_FOUNDATION_CONSISTENCY_REPORT.md](docs/FINAL_FOUNDATION_CONSISTENCY_REPORT.md)
10. [docs/FINAL_FOUNDATION_AUDIT.md](docs/FINAL_FOUNDATION_AUDIT.md)
11. [docs/PHASE5_COMPLETION_GATE.md](docs/PHASE5_COMPLETION_GATE.md)
12. [docs/PARSER_ARCHITECTURE.md](docs/PARSER_ARCHITECTURE.md)
13. [docs/DOCUMENT_EXTRACTION.md](docs/DOCUMENT_EXTRACTION.md)
14. [docs/OFFICIAL_SOURCES.md](docs/OFFICIAL_SOURCES.md)
15. [docs/DECISIONS.md](docs/DECISIONS.md) e arquivos em [docs/adr/](docs/adr/)
16. Regras em [.agents/rules/](.agents/rules/)
17. Código em `src/` e testes em `tests/`.

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

**Próxima Fase:** FASE 6 — Legal RAG & Vector Indexing (**AUTORIZADA**)  
**Versão Atual:** `v0.7.3-foundation-closed`  
**Tarefa Imediata:** 
1. Iniciar o desenvolvimento da FASE 6;
2. Projetar a porta de embeddings e reranker híbrido respeitando a hierarquia jurídica (ADR-0005);
3. Manter 100% da rastreabilidade temporal e proveniência canônica estabelecida na fundação selada.
