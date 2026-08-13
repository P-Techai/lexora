# LÉXORA — Handoff do Projeto

Este documento orienta novos agentes de IA e desenvolvedores sobre como assumir o projeto **LÉXORA (LXR)** sem perda de contexto ou violação da Constituição.

---

# 1. Status do Projeto

- **Fase Atual:** FASE 5 — CLOSED (Fundação Selada e Auditada)
- **Versão Atual:** `v0.7.1-final-foundation`
- **Próxima Fase Autorizável:** FASE 6 — Legal RAG & Vector Indexing
- **Status da FASE 6:** **`NÃO INICIADA`** (Aguardando Prompt Oficial da Fase 6)

---

# 2. Instruções para Início de Turno (Start Protocol)

Siga o checklist do [.agents/workflows/start_session.md](.agents/workflows/start_session.md) e leia na seguinte ordem:

1. [README.md](README.md)
2. [docs/PROJECT.md](docs/PROJECT.md)
3. [docs/PROJECT_MEMORY.md](docs/PROJECT_MEMORY.md)
4. [docs/AGENT_PROTOCOL.md](docs/AGENT_PROTOCOL.md)
5. [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md)
6. [docs/HANDOFF.md](docs/HANDOFF.md)
7. [docs/FINAL_FOUNDATION_AUDIT.md](docs/FINAL_FOUNDATION_AUDIT.md)
8. [docs/PHASE5_COMPLETION_GATE.md](docs/PHASE5_COMPLETION_GATE.md)
9. [docs/PHASE5_PILOT_DATASET.md](docs/PHASE5_PILOT_DATASET.md)
10. [docs/PARSER_ARCHITECTURE.md](docs/PARSER_ARCHITECTURE.md)
11. [docs/DOCUMENT_EXTRACTION.md](docs/DOCUMENT_EXTRACTION.md)
12. [docs/OFFICIAL_SOURCES.md](docs/OFFICIAL_SOURCES.md)
13. [docs/DATABASE_TRUTH_GATE.md](docs/DATABASE_TRUTH_GATE.md)
14. [docs/LEGAL_INTEGRITY_HARDENING_REPORT.md](docs/LEGAL_INTEGRITY_HARDENING_REPORT.md)
15. [docs/TEMPORAL_LEGAL_MODEL.md](docs/TEMPORAL_LEGAL_MODEL.md)
16. [docs/DECISIONS.md](docs/DECISIONS.md) e arquivos em [docs/adr/](docs/adr/)
17. Regras em [.agents/rules/](.agents/rules/)
18. Código em `src/` e testes em `tests/`.

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

**Próxima Fase:** FASE 6 — Legal RAG & Vector Indexing  
**Versão Atual:** `v0.7.1-final-foundation` (Fundação Selada)  
**Tarefa Imediata:** 
1. Aguardar prompt oficial autorizando o início da FASE 6;
2. Projetar a porta de embeddings e reranker híbrido respeitando a hierarquia jurídica (ADR-0005);
3. Manter 100% da rastreabilidade temporal e proveniência canônica estabelecida nas Fases 1 a 5.
