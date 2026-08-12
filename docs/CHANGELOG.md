# LÉXORA — Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.6.5-database-migration-truth] - 2026-08-12

### Adicionado
- **Database Migration Truth Gate (Prompt 06.4):**
  - Documentação da variável `TEST_DATABASE_URL` em `.env.example`.
  - Teste explícito de conectividade PostgreSQL em `tests/integration/test_postgres_connection.py` com `SELECT version();`.
  - Teste de auditoria de catálogo direto via Alembic em `tests/integration/test_postgres_schema_audit.py` (executa exclusivamente `alembic upgrade head` e lê `information_schema.referential_constraints`, decodificando `RESTRICT`, `NO ACTION`, `CASCADE` e `SET NULL`).
  - Teste comportamental dedicado para PostgreSQL real em `tests/integration/test_postgres_evidence_referential_protection.py`.
  - Especificação técnica `docs/DATABASE_TRUTH_GATE.md`.

### Alterado
- **Alembic Test Suite:** Atualizado `tests/integration/test_alembic.py` com integridade da cadeia de scripts (`0001` a `0004`) e teste de round-trip (`upgrade 0004` -> `downgrade 0003` -> `upgrade 0004`).
- **Nomenclatura Honesta de Testes:** Teste auxiliar em SQLite nomeado explicitamente em `tests/integration/test_evidence_referential_protection.py`.

---

## [0.6.4-integrity-verification] - 2026-08-12

### Adicionado
- **PostgreSQL Reality & State Consistency Gate (Prompt 06.3):** Auditoria de schema e portabilidade de links na documentação.

---

## [0.6.3-final-integrity-closure] - 2026-08-12

### Adicionado
- **Final Integrity Closure (Prompt 06.2):** Migration `0004_evidence_fk_integrity.py`, suíte de revogação comportamental, testes de integridade referencial.
