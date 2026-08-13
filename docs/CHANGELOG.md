# LÉXORA — Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.7.3-foundation-closed] - 2026-08-13

### Adicionado
- **Final Foundation Repair & Production Contract Enforcement (Prompt 07.3):**
  - Resolução DNS real (A e AAAA) em `URLSecurityValidator` bloqueando subredes IP privadas, loopback e metadata endpoints.
  - Leitura por streaming em chunks de 64KB com hash SHA-256 incremental e corte por `max_bytes` no `HttpDocumentAcquisitionAdapter`.
  - `SafeRedirectHandler` com limite de 5 redirects, `redirect_chain` capturada e bloqueio de downgrade de HTTPS para HTTP.
  - Identidade lógica canônica determinística (`LegalNode.logical_id`) independente de UUIDs.
  - Suíte de contratos globais em `tests/unit/test_final_foundation_contract.py` e reprodutibilidade em `test_reproducibility_and_reingestion.py`.
  - Especificação `docs/FINAL_FOUNDATION_LOCK.md` e relatório final `docs/FINAL_FOUNDATION_LOCK_REPORT.md` (STATUS: FOUNDATION = CLOSED / FASE 6 = AUTHORIZED).
  - ADR-0014 registrando o contrato de produção da fundação.

---

## [0.7.2-foundation-lock] - 2026-08-13

### Adicionado
- **Final Forensic Correction & Contract Consistency Lock (Prompt 07.2):**
  - Unificação do contrato da porta de aquisição em `DocumentAcquisitionProvider.acquire(request: AcquisitionRequest) -> AcquisitionResult`.
