# LÉXORA — Especificação do Mecanismo de Aquisição (Acquisition Specification)

Este documento descreve os contratos, DTOs e auditorias de captura de artefatos no **LÉXORA (LXR)**.

---

# 1. Contrato de Aquisição (`DocumentAcquisitionProvider`)

A porta `DocumentAcquisitionProvider` desacopla a aplicação do protocolo de rede subjacente:

- **Entrada:** DTO `AcquisitionRequest` (`source_id`, `url`, `max_size_bytes`, `timeout_seconds`, `allowed_content_types`).
- **Saída:** DTO `AcquisitionResult` (`status_code`, `content_type`, `size_bytes`, `raw_bytes`, `content_hash`, `captured_at`, `redirect_chain`).

---

# 2. Revalidação de Redirecionamentos e Sanitização de Auditoria

- **Redirecionamentos:** Se a resposta HTTP contiver redirecionamentos, o `URLSecurityValidator` revalida se o domínio de destino permanece autorizado na allowlist da fonte.
- **Sanitização de Log:** O registro em `AcquisitionAuditLog` grava mensagens de erro higienizadas com no máximo 255 caracteres, garantindo que senhas, tokens ou dados de cabeçalho jamais vazem nos logs.
