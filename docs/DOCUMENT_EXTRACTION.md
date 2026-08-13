# LÉXORA — Especificação de Extração de Documentos (Document Extraction Layer)

Este documento especifica a camada de desacoplamento entre artefatos brutos em disco (`RawArtifact`) e o parser estrutural normativo no **LÉXORA (LXR)**.

---

# 1. Pipeline em 5 Estágios

```text
RAW ARTIFACT (Bytes em Storage)
      ↓
DOCUMENT EXTRACTION (Decodificação de Formato: HTML / TXT / PDF)
      ↓
TEXT NORMALIZATION (Limpeza de Tags & NFKC para busca)
      ↓
STRUCTURAL PARSER (Decomposição em árvore de LegalNodes)
      ↓
TREE VALIDATION (Auditoria de Ciclos e Posições)
      ↓
LEGAL INGESTION (Persistência Canônica + Evidence)
```

---

# 2. Responsabilidades da Interface `DocumentExtractor`

- **Entrada:** `RawArtifact` (bytes brutos e `content_type`).
- **Saída:** `ExtractedDocumentText` contendo o texto extraído limpo e metadados de layout.
- **Isolamento:** A camada de extração não conhece regras normativas (não sabe o que é um Artigo ou Inciso), e o parser estrutural não conhece formatos de arquivos (não sabe o que é HTML, PDF ou HTTP).
