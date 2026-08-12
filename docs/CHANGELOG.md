# LÉXORA — Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.6.3-final-integrity-closure] - 2026-08-12

### Adicionado
- **Final Integrity Closure (Prompt 06.2):**
  - Migration `0004_evidence_fk_integrity.py` aplicando `ON DELETE RESTRICT` nas Foreign Keys da tabela `evidences`.
  - Suíte comportamental de revogação em `tests/unit/test_revocation_behavior.py` (Cenários A, B e C).
  - Teste de integridade referencial de Evidence em banco relacional `tests/integration/test_evidence_referential_protection.py`.
  - Expansão do auditor global de governança em `tests/unit/test_security_governance_audit.py` (inspeciona todas as 8 tabelas/modelos ORM e 4 migrations garantindo 0 CASCADE e 0 SET NULL, além de análise estática de proibições de DELETE).

### Alterado
- **Ajuste de FKs de Evidence:** Alterados os campos `legal_document_id`, `legal_version_id` e `legal_node_id` no modelo ORM `EvidenceModel` de `SET NULL` para `RESTRICT`.
- **Downgrade Determinístico da Migration 0003:** Substituído `pass` por implementação de reversão limpa e determinística em `0003_legal_integrity_hardening.py`.

---

## [0.6.2-legal-integrity-hardening] - 2026-08-12

### Adicionado
- **Hardening de Integridade Jurídica (Prompt 06.1):** Exceção `MissingRevokingSourceError`, migration `0003_legal_integrity_hardening.py`, auditoria automatizada e ADR-0012.

---

## [0.6.1-readiness-audit] - 2026-08-12

### Adicionado
- **Auditoria de Prontidão (Prompt 06):** `docs/LEGAL_TRUTH_READINESS.md`, `ADR-0011` e testes de cenários históricos golden.
