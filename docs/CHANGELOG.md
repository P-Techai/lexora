# LÉXORA — Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.6.4-integrity-verification] - 2026-08-12

### Adicionado
- **PostgreSQL Reality & State Consistency Gate (Prompt 06.3):**
  - Teste de auditoria de catálogo relacional direto em `tests/integration/test_postgres_schema_audit.py` (inspeciona o schema no `HEAD` / `0004` garantindo `CASCADE = 0` e `SET NULL = 0`).
  - Suporte a execução Dual em `tests/integration/test_evidence_referential_protection.py` (SQLite como auxiliar rápido e PostgreSQL via `TEST_DATABASE_URL` como autoritativo).

### Alterado
- **Portabilidade de Documentação:**
  - Substituição de todos os links absolutos (`file:///c:/Users/Pedro/...`) por caminhos relativos do repositório em `docs/HANDOFF.md` e documentação operacional.
- **Clarificação de Estado no Handoff:**
  - `docs/HANDOFF.md` atualizado para declarar `Fase Atual: FASE 06.3`, `Próxima fase autorizável: FASE 5`, `FASE 5: NÃO INICIADA`.

---

## [0.6.3-final-integrity-closure] - 2026-08-12

### Adicionado
- **Final Integrity Closure (Prompt 06.2):** Migration `0004_evidence_fk_integrity.py`, suíte de revogação comportamental, testes de integridade referencial.

---

## [0.6.2-legal-integrity-hardening] - 2026-08-12

### Adicionado
- **Hardening de Integridade Jurídica (Prompt 06.1):** Exceção `MissingRevokingSourceError`, migration `0003_legal_integrity_hardening.py`, auditoria automatizada e ADR-0012.

---

## [0.6.1-readiness-audit] - 2026-08-12

### Adicionado
- **Auditoria de Prontidão (Prompt 06):** `docs/LEGAL_TRUTH_READINESS.md`, `ADR-0011` e testes de cenários históricos golden.
