# LÉXORA — Especificação do Pipeline de Ingestão Jurídica (Ingestion Specification)

Este documento descreve os contratos, estágios e garantias de qualidade do pipeline de ingestão de documentos normativos do **LÉXORA (LXR)**.

---

# 1. Fluxo do Pipeline Determinístico

Nenhum documento externo é adicionado à Base de Conhecimento sem transitar pelos 7 estágios obrigatórios:

```
[1. RAW CONTENT] ──> [2. HASH SHA-256] ──> [3. NORMALIZAÇÃO UNICODE] ──> [4. METADATA VALIDATION]
                                                                                │
[7. PERSISTÊNCIA] <── [6. ÁRVORE INTEGRITY] <── [5. STRUCTURAL PARSER] <───────┘
```

---

# 2. Garantias Invioláveis do Pipeline

1. **Idempotência Total:** Solicitações repetidas da mesma norma com o mesmo hash retornam status `DUPLICATE` sem gerar registros duplicados no banco.
2. **Preservação do Raw:** O conteúdo bruto original é armazenado intacto e imutável no armazenamento seguro (`StorageProvider`). A normalização afeta apenas o texto processável.
3. **Auditabilidade por Hash:** Todo documento, versão e nó normativo possui seu hash SHA-256 gravado no atributo `content_hash`.
4. **Modo Diagnóstico (`dry_run=True`):** Permite validar a integridade estrutural, a sintaxe do parser e gerar relatórios de erro sem gravar nenhuma linha no banco de dados.

---

# 3. Contrato DTO (`LegalDocumentIngestionRequest` & `LegalDocumentIngestionResult`)

### Request DTO
```json
{
  "source_id": "src-planalto",
  "document_type": "ORDINARY_LAW",
  "document_number": "8112",
  "title": "Lei nº 8.112, de 11 de dezembro de 1990",
  "ementa": "Dispõe sobre o regime jurídico dos servidores...",
  "jurisdiction": "FEDERAL",
  "issuing_body": "PRESIDENCIA_DA_REPUBLICA",
  "publication_date": "1990-12-12",
  "official_url": "https://www.planalto.gov.br/...",
  "raw_content": "Art. 1º Esta Lei institui o Regime Jurídico...",
  "content_type": "text/plain"
}
```

### Result DTO
```json
{
  "status": "CREATED",
  "document_id": "uuid-doc",
  "version_id": "uuid-ver",
  "content_hash": "sha256-hash-do-conteudo",
  "created": true,
  "duplicate": false,
  "validation_errors": [],
  "warnings": []
}
```
