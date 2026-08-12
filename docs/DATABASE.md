# LÉXORA — Especificação do Banco de Dados PostgreSQL

Este documento especifica a infraestrutura de banco de dados do **LÉXORA (LXR)** em PostgreSQL 16 + `pgvector`.

---

# 1. Esquema Relacional e Tabelas

### 1. `sources`
- `id` (VARCHAR(36), PK)
- `name` (VARCHAR(255), NOT NULL)
- `official` (BOOLEAN, DEFAULT TRUE)
- `authority_level` (INTEGER, CHECK >= 1 AND <= 5)
- `base_url` (VARCHAR(1024))
- `jurisdiction` (VARCHAR(50), DEFAULT 'FEDERAL')
- `active` (BOOLEAN, DEFAULT TRUE)
- `created_at`, `updated_at` (TIMESTAMP)

### 2. `legal_documents`
- `id` (VARCHAR(36), PK)
- `source_id` (VARCHAR(36), FK -> `sources.id` RESTRICT)
- `document_type` (VARCHAR(50), NOT NULL)
- `document_number` (VARCHAR(100), NOT NULL)
- `title` (VARCHAR(512), NOT NULL)
- `ementa` (TEXT)
- `jurisdiction` (VARCHAR(50), DEFAULT 'FEDERAL')
- `issuing_body` (VARCHAR(255), NOT NULL)
- `publication_date` (DATE)
- `official_url` (VARCHAR(1024))
- `document_hash` (VARCHAR(64), NOT NULL)
- `created_at`, `updated_at` (TIMESTAMP)

### 3. `legal_versions`
- `id` (VARCHAR(36), PK)
- `legal_document_id` (VARCHAR(36), FK -> `legal_documents.id` CASCADE)
- `version_number` (INTEGER, DEFAULT 1)
- `content_hash` (VARCHAR(64), NOT NULL)
- `published_at`, `effective_from`, `effective_until` (DATE)
- `status` (VARCHAR(50), DEFAULT 'ACTIVE')
- `source_document_url` (VARCHAR(1024))
- `raw_storage_key` (VARCHAR(512))
- `parser_version` (VARCHAR(50), DEFAULT '1.0.0')
- `created_at` (TIMESTAMP)
- **Constraint:** `CHECK (effective_until IS NULL OR effective_from IS NULL OR effective_until >= effective_from)`

### 4. `legal_nodes`
- `id` (VARCHAR(36), PK)
- `legal_version_id` (VARCHAR(36), FK -> `legal_versions.id` CASCADE)
- `parent_id` (VARCHAR(36), FK -> `legal_nodes.id` CASCADE, NULL para raiz)
- `node_type` (VARCHAR(50), NOT NULL)
- `identifier` (VARCHAR(100), NOT NULL)
- `label` (VARCHAR(255), NOT NULL)
- `text` (TEXT, NOT NULL)
- `normalized_text` (TEXT)
- `path` (VARCHAR(1024), NOT NULL)
- `position` (INTEGER, DEFAULT 1)
- `content_hash` (VARCHAR(64), NOT NULL)
- `effective_from`, `effective_until` (DATE)
- `status` (VARCHAR(50), DEFAULT 'ACTIVE')
- `metadata` (JSON, DEFAULT '{}')
- `created_at`, `updated_at` (TIMESTAMP)

### 5. `evidences`
- `id` (VARCHAR(36), PK)
- `source_id` (VARCHAR(36), FK -> `sources.id` RESTRICT)
- `legal_document_id` (VARCHAR(36), FK -> `legal_documents.id` SET NULL)
- `legal_version_id` (VARCHAR(36), FK -> `legal_versions.id` SET NULL)
- `legal_node_id` (VARCHAR(36), FK -> `legal_nodes.id` SET NULL)
- `source_url` (VARCHAR(1024))
- `quote_or_excerpt` (TEXT, NOT NULL)
- `locator` (VARCHAR(255))
- `content_hash` (VARCHAR(64), NOT NULL)
- `captured_at`, `created_at` (TIMESTAMP)

### 6. `legal_relations`
- `id` (VARCHAR(36), PK)
- `source_node_id` (VARCHAR(36), FK -> `legal_nodes.id` CASCADE)
- `target_node_id` (VARCHAR(36), FK -> `legal_nodes.id` CASCADE)
- `relation_type` (VARCHAR(50), NOT NULL)
- `effective_from`, `effective_until` (DATE)
- `confidence` (FLOAT, DEFAULT 1.0, CHECK >= 0.0 AND <= 1.0)
- `evidence_id` (VARCHAR(36), FK -> `evidences.id` SET NULL)
- `created_at`, `updated_at` (TIMESTAMP)
- **Constraint:** `CHECK (source_node_id != target_node_id)`

---

# 2. Estratégia de Migrations via Alembic

 As migrations são gerenciadas pelo Alembic no diretório `alembic/versions/`.
- Executar migrations online (assíncrono via `asyncpg`).
- Suporte total a ciclo de reversão (`alembic upgrade head`, `alembic downgrade base`).
