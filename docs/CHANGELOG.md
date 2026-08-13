# LÉXORA — Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.8.1-retrieval-production-closure] - 2026-08-13

### Adicionado
- **Retrieval Implementation Closure & Production-Grade RAG Foundation (Prompt 08.1):**
  - Endpoint HTTP `/api/v1/legal/retrieve` refatorado para executar a classe de uso real `RetrieveLegalInformationUseCase` contra os repositórios relacionais.
  - Migration Alembic `0007_phase6_vector_fts.py` habilitando a extensão `vector` (pgvector) e a coluna `search_vector` (tsvector) para FTS nativo no PostgreSQL.
  - `EmbeddingProviderFactory` para carregamento de provedores por variáveis de ambiente, com bloqueio estrito de fallbacks silenciosos para mocks em produção.
  - Critério de desempate determinístico estável (`score DESC, content_hash ASC, legal_node_id ASC`).
  - Suíte de testes de integração E2E `tests/integration/test_phase6_retrieval_end_to_end.py` (com chamadas HTTP reais e verificação de determinismo 10x).
  - Auditoria estática de código produtivo `tests/unit/test_no_production_stubs.py` (0 stubs em `src/`).
  - Relatório final `docs/PHASE6_1_RETRIEVAL_PRODUCTION_CLOSURE.md` (STATUS: FASE 6.1 = COMPLETE / FASE 6.2 = AUTHORIZED).

---

## [0.8.0-retrieval-foundation] - 2026-08-13

### Adicionado
- **Phase 6.1 — Hybrid Legal Retrieval & RAG Foundation (Prompt 08):**
  - Declarada a porta `EmbeddingProvider` em `src/application/ports/embedding_provider.py` com o adaptador determinístico `MockEmbeddingProvider` (1536 dimensões).
