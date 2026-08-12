# LÉXORA — Especificação do Gate de Verdade de Migrações de Banco de Dados (Database Migration Truth Gate)

**Versão do Documento:** `v0.6.5-database-migration-truth`  
**Data:** 2026-08-12  
**Status da Fase:** `FASE 06.4 — PASS`

---

# 1. A Cadeia de Confiança de 5 Estágios da LÉXORA

Para o projeto **LÉXORA (LXR)**, a declaração de Verdade Jurídica e Integridade Referencial não pode depender de suposições ou abstrações parciais. A arquitetura estabelece a seguinte cadeia inquebrável de validação:

```text
1. CÓDIGO FONTE (ORM)
        │
        ▼
2. MIGRATIONS ALEMBIC (Cadeia 0001 -> 0002 -> 0003 -> 0004)
        │
        ▼
3. BANCO POSTGRESQL REAL (Ambiente Isolado via TEST_DATABASE_URL)
        │
        ▼
4. CATÁLOGO DO POSTGRESQL (information_schema / pg_constraint)
        │
        ▼
5. TESTES COMPORTAMENTAIS (Tentativa física de violação de FK -> IntegrityError RESTRICT)
```

---

# 2. Distinção entre Metadados ORM, Migrations e o Catálogo do Banco

| Camada | Escopo | Papel na Validação |
| :--- | :--- | :--- |
| **ORM Metadata (`Base.metadata`)** | Código Python local | Define a intenção das entidades no aplicativo. Não é garantia de schema no banco relacional. |
| **Alembic Migrations (`alembic/versions/`)** | Scripts DDL versionados | Define as alterações estruturais sequenciais de schema (`0001` a `0004`). |
| **Catálogo PostgreSQL (`information_schema`)** | Schema DDL em execução | **Verdade Operacional Autoritativa.** Registra a ação real de Foreign Key (`delete_rule`). |
| **Teste Comportamental** | Execução de SQL real | Prova empírica de que a operação destrutiva é REJEITADA com `RESTRICT`. |

---

# 3. Regra de Proibição de Fallbacks Silenciosos

- Testes nomeados com sufixo/prefixo PostgreSQL **NUNCA** realizam fallback silencioso para SQLite em memória se o PostgreSQL não estiver disponível.
- Se `TEST_DATABASE_URL` não for fornecida ou apontar para um motor não-PostgreSQL, os testes com sufixo PostgreSQL falham explicitamente (`FAIL / BLOCKED`).
- Testes em SQLite são mantidos exclusivamente sob nomenclaturas auxiliares explícitas (ex.: `test_sqlite_auxiliary_...`).

---

# 4. Estado Atual das Foreign Keys de Evidência e Domínio no HEAD (`0004`)

Após a aplicação da migration `0004_evidence_fk_integrity.py` (`alembic upgrade head`), o catálogo real do PostgreSQL registra:

- `evidences.legal_document_id` $\to$ `RESTRICT` (`CASCADE = 0`, `SET NULL = 0`)
- `evidences.legal_version_id` $\to$ `RESTRICT` (`CASCADE = 0`, `SET NULL = 0`)
- `evidences.legal_node_id` $\to$ `RESTRICT` (`CASCADE = 0`, `SET NULL = 0`)
- `legal_versions.legal_document_id` $\to$ `RESTRICT` (`CASCADE = 0`, `SET NULL = 0`)
- `legal_nodes.legal_version_id` $\to$ `RESTRICT` (`CASCADE = 0`, `SET NULL = 0`)
- `legal_nodes.parent_id` $\to$ `RESTRICT` (`CASCADE = 0`, `SET NULL = 0`)
- `legal_relations.source_node_id` $\to$ `RESTRICT` (`CASCADE = 0`, `SET NULL = 0`)
- `legal_relations.target_node_id` $\to$ `RESTRICT` (`CASCADE = 0`, `SET NULL = 0`)

---

# 5. Status das Infraestruturas Cloud

- **Neon PostgreSQL:** NÃO INTEGRADO
- **Supabase Storage/DB:** NÃO INTEGRADO
- **Cloudflare R2/Workers:** NÃO INTEGRADO
