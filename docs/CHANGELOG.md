# LÉXORA — Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.8.0-retrieval-foundation] - 2026-08-13

### Adicionado
- **Phase 6.1 — Hybrid Legal Retrieval & RAG Foundation (Prompt 08):**
  - Declarada a porta `EmbeddingProvider` em `src/application/ports/embedding_provider.py` com o adaptador determinístico `MockEmbeddingProvider` (1536 dimensões).
  - Entidade `LegalEmbedding` e modelo ORM `LegalEmbeddingModel` mapeando a tabela `legal_node_embeddings` com restrição `UNIQUE` de idempotência.
  - Construtor canônico de texto de recuperação (`CanonicalRetrievalTextBuilder`) agregando o contexto da hierarquia ancestral.
  - Serviço de indexação `LegalEmbeddingIndexer` para geração e persistência de vetores.
  - Normalizador de consultas `LegalQueryNormalizer` e extração de identificadores normativos sem o uso de LLMs.
  - Serviço de busca híbrida `HybridLegalRetrievalService` com fusão lexical + semântica, reranking determinístico, filtragem temporal de vigência (`TemporalIntegrityValidator`) e validação da cadeia de proveniência em 5 níveis.
  - Endpoint da API `POST /api/v1/legal/retrieve` publicado na FastAPI.
  - Migration Alembic `0006_phase6_retrieval.py`.
  - Suíte de testes unitários e de integração `test_golden_temporal_provenance_retrieval.py`.
  - Especificação `docs/RETRIEVAL_ARCHITECTURE.md`, relatório `docs/PHASE6_1_COMPLETION.md` e ADR-0015.

---

## [0.7.3-foundation-closed] - 2026-08-13

### Adicionado
- **Final Foundation Repair & Production Contract Enforcement (Prompt 07.3):**
  - Resolução DNS real (A e AAAA) em `URLSecurityValidator`.
