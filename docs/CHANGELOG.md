# LÉXORA — Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.7.1-final-foundation] - 2026-08-13

### Adicionado
- **Final Forensic Audit & Production Foundation Lock (Prompt 07.1):**
  - Verificação AST-level de pureza do domínio em `tests/unit/test_forensic_foundation_audit.py` (zero dependências de ORMs, clientes HTTP ou SDKs em `src/domain/`).
  - Hash canônico determinístico para `LegalNode` em `DocumentHashCalculator.calculate_canonical_node_hash` (independente de UUIDs e IDs de banco).
  - Proteção SSRF em redirects HTTP via `SafeRedirectHandler` em `HttpDocumentAcquisitionAdapter`.
  - Auditoria estática de imutabilidade jurídica confirmando zero comandos SQL DELETE em entidades normativas.
  - Relatório final de selamento da fundação `docs/FINAL_FOUNDATION_AUDIT.md` (STATUS: PASS).

---

## [0.7.0-official-ingestion-pilot] - 2026-08-13

### Adicionado
- **Fase 5 — Ingestão Oficial de Legislação Brasileira Real:**
  - Configuração do Neon PostgreSQL via driver `asyncpg` nas variáveis `DATABASE_URL` e `TEST_DATABASE_URL`.
  - Adaptador `HttpDocumentAcquisitionAdapter` com SSRF e rate limiting.
  - Parser estrutural `BrazilianLawParser` (`brazilian-law-parser@1.0.0`).
