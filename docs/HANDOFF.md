# LÉXORA — Handoff do Projeto

Este documento orienta novos agentes de IA e desenvolvedores sobre como assumir o projeto **LÉXORA (LXR)** sem perda de contexto ou violação da Constituição.

---

# 1. Status do Projeto

- **Fase Atual:** FASE 06.4 — Database Migration Truth Gate
- **Versão Atual:** `v0.6.5-database-migration-truth`
- **Próxima Fase Autorizável:** FASE 5 — Ingestão Oficial & Parsers de Legislação Real Brasileira
- **Status da FASE 5:** **`NÃO INICIADA`** (Aguardando Prompt da Fase 5)

---

# 2. Instruções para Início de Turno (Start Protocol)

Siga o checklist do [.agents/workflows/start_session.md](.agents/workflows/start_session.md) e leia na seguinte ordem:

1. [README.md](README.md)
2. [docs/PROJECT.md](docs/PROJECT.md)
3. [docs/PROJECT_MEMORY.md](docs/PROJECT_MEMORY.md)
4. [docs/AGENT_PROTOCOL.md](docs/AGENT_PROTOCOL.md)
5. [docs/CURRENT_STATE.md](docs/CURRENT_STATE.md)
6. [docs/HANDOFF.md](docs/HANDOFF.md)
7. [docs/DATABASE_TRUTH_GATE.md](docs/DATABASE_TRUTH_GATE.md)
8. [docs/LEGAL_INTEGRITY_HARDENING_REPORT.md](docs/LEGAL_INTEGRITY_HARDENING_REPORT.md)
9. [docs/LEGAL_INTEGRITY_HARDENING.md](docs/LEGAL_INTEGRITY_HARDENING.md)
10. [docs/TEMPORAL_LEGAL_MODEL.md](docs/TEMPORAL_LEGAL_MODEL.md)
11. [docs/SOURCE_GOVERNANCE.md](docs/SOURCE_GOVERNANCE.md)
12. [docs/ACQUISITION.md](docs/ACQUISITION.md)
13. [docs/RAW_ARTIFACTS.md](docs/RAW_ARTIFACTS.md)
14. [docs/INGESTION.md](docs/INGESTION.md)
15. [docs/LEGAL_INTEGRITY.md](docs/LEGAL_INTEGRITY.md)
16. [docs/LEGAL_MODEL.md](docs/LEGAL_MODEL.md)
17. [docs/DATABASE.md](docs/DATABASE.md)
18. [docs/DECISIONS.md](docs/DECISIONS.md) e arquivos em [docs/adr/](docs/adr/)
19. Regras em [.agents/rules/](.agents/rules/)
20. Código em `src/` e testes em `tests/`.

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

**Próxima Fase:** FASE 5 — Ingestão Oficial & Parsers de Legislação Real Brasileira  
**Versão:** `v0.6.5-database-migration-truth` (Gate 06.4 Concluído)  
**Tarefa Imediata:** 
1. Implementar os conectores de leitura sintética/mock para atuar sobre a estrutura da Constituição Federal e Leis Complementares;
2. Desenvolver os parsers normativos capazes de extrair a hierarquia real de artigos, parágrafos, incisos e alíneas;
3. Integrar a ingestão oficial com o pipeline determinístico e temporal construído nas Fases 1-4.
