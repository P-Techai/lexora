# LÉXORA — Especificação de Artefatos Brutos (Raw Artifacts Specification)

Este documento estabelece o gerenciamento, imutabilidade e armazenamento de artefatos brutos no **LÉXORA (LXR)**.

---

# 1. Distinção Crucial: `RawArtifact` x `LegalDocument`

- **`RawArtifact`:** Representa os bytes brutos imutáveis capturados da fonte externa (PDF, HTML, XML, JSON), identificados pelo seu hash SHA-256 e referência no `StorageProvider`.
- **`LegalDocument`:** Representa a entidade documental jurídica abstrata cadastrada após a validação de metadados.

---

# 2. Rastreabilidade e Reprodutibilidade

Todo `RawArtifact` garante a resposta para a auditoria:
- De onde veio? (`source_id`, `url`);
- Quando foi capturado? (`captured_at`);
- Qual o conteúdo exato? (`content_hash` SHA-256);
- Onde está armazenado? (`storage_key` no `StorageProvider`).
