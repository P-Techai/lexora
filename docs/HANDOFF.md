# LÉXORA — Handoff do Projeto

Este documento orienta novos agentes de IA e desenvolvedores sobre como assumir o projeto **LÉXORA (LXR)** sem perda de contexto ou violação da Constituição.

---

# 1. Instruções para Início de Turno (Start Protocol)

Siga o checklist do [.agents/workflows/start_session.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/.agents/workflows/start_session.md) e leia na seguinte ordem:

1. [README.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/README.md)
2. [docs/PROJECT.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/PROJECT.md)
3. [docs/PROJECT_MEMORY.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/PROJECT_MEMORY.md)
4. [docs/AGENT_PROTOCOL.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/AGENT_PROTOCOL.md)
5. [docs/CURRENT_STATE.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/CURRENT_STATE.md)
6. [docs/HANDOFF.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/HANDOFF.md)
7. [docs/LEGAL_INTEGRITY_HARDENING_REPORT.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/LEGAL_INTEGRITY_HARDENING_REPORT.md)
8. [docs/LEGAL_INTEGRITY_HARDENING.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/LEGAL_INTEGRITY_HARDENING.md)
9. [docs/TEMPORAL_LEGAL_MODEL.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/TEMPORAL_LEGAL_MODEL.md)
10. [docs/SOURCE_GOVERNANCE.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/SOURCE_GOVERNANCE.md)
11. [docs/ACQUISITION.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/ACQUISITION.md)
12. [docs/RAW_ARTIFACTS.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/RAW_ARTIFACTS.md)
13. [docs/INGESTION.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/INGESTION.md)
14. [docs/LEGAL_INTEGRITY.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/LEGAL_INTEGRITY.md)
15. [docs/LEGAL_MODEL.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/LEGAL_MODEL.md)
16. [docs/DATABASE.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/DATABASE.md)
17. [docs/DECISIONS.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/DECISIONS.md) e arquivos em [docs/adr/](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/adr/)
18. Regras em [.agents/rules/](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/.agents/rules/)
19. Código em `src/` e testes em `tests/`.

---

# 2. Checklist de Finalização de Tarefa (End Protocol)

- [ ] Executar testes unitários e de integração (`pytest`);
- [ ] Atualizar `docs/CHANGELOG.md`;
- [ ] Atualizar `docs/CURRENT_STATE.md`;
- [ ] Atualizar `docs/HANDOFF.md` com o próximo passo prioritário;
- [ ] Criar novo ADR em `docs/adr/` se uma decisão arquitetural foi tomada;
- [ ] Apresentar o Relatório Final com os itens obrigatórios da entrega.

---

# 3. Próximo Passo Prioritário

**Fase Atual:** FASE 5 — Ingestão Oficial & Parsers de Legislação Real Brasileira  
**Versão Atual:** `v0.6.2-legal-integrity-hardening`  
**Tarefa Imediata:** 
1. Implementar os conectores de leitura sintética/mock para atuar sobre a estrutura da Constituição Federal e Leis Complementares;
2. Desenvolver os parsers normativos capazes de extrair a hierarquia real de artigos, parágrafos, incisos e alíneas;
3. Integrar a ingestão oficial com o pipeline determinístico e temporal construído nas Fases 1-4.
