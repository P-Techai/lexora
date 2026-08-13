# LÉXORA — Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.7.2-foundation-lock] - 2026-08-13

### Adicionado
- **Final Forensic Correction & Contract Consistency Lock (Prompt 07.2):**
  - Unificação do contrato da porta de aquisição em `DocumentAcquisitionProvider.acquire(request: AcquisitionRequest) -> AcquisitionResult`.
  - Inclusão dos DTOs `AcquisitionRequest` e `AcquisitionResult` com `redirect_chain` para auditoria.
  - Alinhamento do enum `ChangeStatus` (`NEW`, `UNCHANGED`, `CHANGED`, `REMOVED`, `UNAVAILABLE`).
  - Desestruturação da tupla `(nodes, parser_warnings)` no `IngestDocumentUseCase` enviando apenas a lista de `LegalNode` para gravação.
  - Suporte a `SUBSECAO` e `ANEXO` no `BrazilianLawParser` com avisos estruturados `ParserWarning`.
  - Suíte de testes E2E em `tests/integration/test_end_to_end_acquisition_ingestion.py`.
  - Suíte de testes de concorrência e race condition em `tests/integration/test_concurrency_race_conditions.py`.
  - Relatório final de consistência `docs/FINAL_FOUNDATION_CONSISTENCY_REPORT.md` (STATUS: PASS).

---

## [0.7.1-final-foundation] - 2026-08-13

### Adicionado
- **Final Forensic Audit & Production Foundation Lock (Prompt 07.1):**
  - Verificação AST-level de pureza do domínio em `tests/unit/test_forensic_foundation_audit.py`.
