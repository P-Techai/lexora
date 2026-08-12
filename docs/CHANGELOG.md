# LÉXORA — Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.6.2-legal-integrity-hardening] - 2026-08-12

### Adicionado
- **Hardening de Integridade Jurídica (Prompt 06.1):**
  - Exceção de domínio `MissingRevokingSourceError` para rejeitar criação de relações de revogação sem ato revogador distinto.
  - Migration corretiva `0003_legal_integrity_hardening.py` alterando todas as Foreign Keys com `CASCADE` nas tabelas jurídicas para `ON DELETE RESTRICT`.
  - Suíte automatizada de segurança de governança em `tests/unit/test_security_governance_audit.py` que verifica 0 `CASCADE` em modelos ORM, centralização da matemática temporal e proibição de auto-revogações.
  - `ADR-0012-legal-integrity-hardening.md` (ADR-0012).
  - `docs/LEGAL_INTEGRITY_HARDENING.md` e `docs/LEGAL_INTEGRITY_HARDENING_REPORT.md` (STATUS: FASE 06.1 — PASS).

### Alterado
- **Eliminação de ON DELETE CASCADE:** Alterados todos os modelos ORM (`LegalVersionModel`, `LegalNodeModel`, `LegalRelationModel`) para `ondelete="RESTRICT"`.
- **Fonte Única de Matemática Temporal:** Centralizada a semântica semi-aberta em `TemporalIntegrityValidator.is_date_in_range(target_date, effective_from, effective_until)` $[effective\_from, effective\_until)$. `LegalVersion.is_effective_on()` e `TemporalLegalSearchService` delegam exclusivamente a essa função.
- **Proibição de Auto-Revogação:** `RevokeLegalDocumentUseCase` e `RevokeLegalNodeUseCase` disparam `MissingRevokingSourceError` caso `revoking_node_id` não seja informado ou seja idêntico ao nó alvo.

---

## [0.6.1-readiness-audit] - 2026-08-12

### Adicionado
- **Auditoria de Prontidão (Prompt 06):** `docs/LEGAL_TRUTH_READINESS.md`, `ADR-0011` e testes de cenários históricos golden.

---

## [0.6.0-temporal-truth] - 2026-08-12

### Adicionado
- **Advanced Legal Versioning & Temporal Truth (Fase 4):** `TemporalIntegrityValidator`, `TemporalLegalSearchService`, `QueryLegalAtDateUseCase`, `RevokeLegalDocumentUseCase`, `RevokeLegalNodeUseCase`.
