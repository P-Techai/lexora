# LÉXORA — Processamento em Lote de NF-e (`NFeBatchProcessing`)

Este documento descreve a arquitetura de processamento em lote de NF-e do **LÉXORA (LXR)** na **FASE 8**.

---

# 1. Pipeline de Processamento em Lote (`POST /api/v1/fiscal/nfe/batch`)

1. **Recepção:** Recebe uma lista de payloads XML de NF-e vinculadas a uma empresa (`company_id`).
2. **Validação & Deduplicação:** Remove arquivos duplicados dentro do lote com base na chave de acesso e no hash do XML.
3. **Resiliência por Item:** Cada XML é analisado individualmente. Falhas de formatação em um XML não afetam o processamento dos demais itens do lote.
4. **Estados do Lote (`BatchStatus`):** `RECEIVED`, `VALIDATING`, `PROCESSING`, `COMPLETED`, `PARTIAL`, `REQUIRES_REVIEW`, `FAILED`, `REJECTED`.
