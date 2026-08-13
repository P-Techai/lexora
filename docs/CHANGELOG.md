# LÉXORA — Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.7.0-official-ingestion-pilot] - 2026-08-13

### Adicionado
- **Fase 5 — Ingestão Oficial de Legislação Brasileira Real:**
  - Configuração do Neon PostgreSQL via driver `asyncpg` nas variáveis `DATABASE_URL` e `TEST_DATABASE_URL`.
  - Porta `DocumentExtractor` e adaptador `HtmlTxtDocumentExtractor` para decodificação de formatos de arquivos.
  - Adaptador real `HttpDocumentAcquisitionAdapter` com proteção SSRF, rate limiting polido e audit log.
  - Parser estrutural `BrazilianLawParser` (`brazilian-law-parser@1.0.0`) com suporte a hierarquia completa (`NORMA` a `ITEM`) e numerações reais brasileiras.
  - Nó raiz `NORMA` determinístico eliminando dependência informal de `nodes[0]`.
  - Migration Alembic `0005_phase5_normative_acts.py` com `upgrade()` e `downgrade()`.
  - Dataset piloto registrado em `docs/PHASE5_PILOT_DATASET.md` e testes golden em `tests/integration/test_golden_pilot_documents.py`.
  - Documentação completa: `OFFICIAL_SOURCES.md`, `PARSER_ARCHITECTURE.md`, `DOCUMENT_EXTRACTION.md`, `PHASE5_PILOT_DATASET.md`, `PHASE5_COMPLETION_GATE.md` (STATUS: PASS) e `ADR-0013`.

---

## [0.6.5-database-migration-truth] - 2026-08-12

### Adicionado
- **Database Migration Truth Gate (Prompt 06.4):** Testes diretos de catálogo PostgreSQL via Alembic `0004` no HEAD.
