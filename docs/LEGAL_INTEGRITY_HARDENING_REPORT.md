# LÉXORA — RELATÓRIO DE INTEGRIDADE JURÍDICA E AUDITORIA FORENSE

**Status Final:** **`FASE 5 — CLOSED (PASS)`**  
**Versão Final:** `v0.7.1-final-foundation`  
**Data de Conclusão:** 2026-08-13  
**Confirmação de Escopo:** **`FASE 6 NÃO INICIADA`**

---

## 1. Status

**`PASS`**

---

## 2. PostgreSQL / Neon Utilizado

- Motor PostgreSQL real (Neon Database Pooler) auditado via `DATABASE_URL` e `TEST_DATABASE_URL` com driver `asyncpg`.
- Conexão e dialeto validados via `SELECT version();` no arquivo `tests/integration/test_postgres_connection.py`.

---

## 3. Confirmação de TEST_DATABASE_URL

- Variáveis `DATABASE_URL` e `TEST_DATABASE_URL` documentadas oficialmente em `.env.example` e configuradas no `.env`.
- Proibição absoluta de fallbacks silenciosos para SQLite em testes nomeados como PostgreSQL.

---

## 4. Migration Head

- Revision HEAD Efetivo: `0005_phase5_normative_acts`.

---

## 5. Resultado Alembic

- `alembic upgrade head` executado sobre a URL síncrona do banco de dados relacional.
- `alembic current` confirma o revision head `0005_phase5_normative_acts`.

---

## 6. Catálogo PostgreSQL Auditado

- Schema construído **estritamente via Alembic** (`alembic upgrade head`), sem utilizar `Base.metadata.create_all()`. Catálogo do PostgreSQL consultado diretamente em `information_schema.referential_constraints`.

---

## 7. ON DELETE por Constraint Decodificadas Efetivamente

- `evidences.legal_document_id` $\to$ **`RESTRICT`** (`CASCADE = 0`, `SET NULL = 0`)
- `evidences.legal_version_id` $\to$ **`RESTRICT`** (`CASCADE = 0`, `SET NULL = 0`)
- `evidences.legal_node_id` $\to$ **`RESTRICT`** (`CASCADE = 0`, `SET NULL = 0`)
- `legal_versions.legal_document_id` $\to$ **`RESTRICT`** (`CASCADE = 0`, `SET NULL = 0`)
- `legal_nodes.legal_version_id` $\to$ **`RESTRICT`** (`CASCADE = 0`, `SET NULL = 0`)
- `legal_nodes.parent_id` $\to$ **`RESTRICT`** (`CASCADE = 0`, `SET NULL = 0`)
- `legal_relations.source_node_id` $\to$ **`RESTRICT`** (`CASCADE = 0`, `SET NULL = 0`)
- `legal_relations.target_node_id` $\to$ **`RESTRICT`** (`CASCADE = 0`, `SET NULL = 0`)

---

## 8. Evidence Tests em PostgreSQL Real

- Inserção de Source, Document, Version, Node e Evidence em banco migrado via Alembic. Rejeição física comprovada (`IntegrityError` / `RESTRICT`) ao tentar deletar `LegalDocument`, `LegalVersion` ou `LegalNode`.

---

## 9. Migration Round-Trip

- Cadeia `0001` $\to$ `0002` $\to$ `0003` $\to$ `0004` $\to$ `0005` (`HEAD`) validada.
- Round-trip `upgrade head` $\to$ `downgrade 0004` $\to$ `upgrade head` exercitado com sucesso.

---

## 10. Revocation Tests

- Cenário A (`revoking_node_id = None`): `MissingRevokingSourceError` (PASS).
- Cenário B (`revoking_node_id == target_node_id`): `MissingRevokingSourceError` (PASS).
- Cenário C ($B \neq A$): Cria relação `B REVOKES A` sem auto-relação (PASS).

---

## 11. Temporal Tests

- Matemática $[effective\_from, effective\_until)$ mantida em `TemporalIntegrityValidator.is_date_in_range`.
- $T == effective\_until \implies \text{NOT EFFECTIVE}$. Proibição de `datetime.now()` implícito mantida.

---

## 12. Pureza do Domínio AST & DELETE Audit

- Busca estática em AST realizada em `src/domain/`. Confirmado **0** imports de ORMs, clientes HTTP ou SDKs.
- Busca estática realizada em `src/`. Confirmado **0** comandos de delete físico sobre tabelas normativas.

---

## 13. Testes Completo

- **STATUS:** `PASS`
- **FAIL:** 0
- **SKIPPED de Integridade:** 0

---

## 14. FAILED

- **0**

---

## 15. SKIPPED

- **0**

---

## 16. Limitações

- Nenhuma limitação impeditiva. A fundação da LÉXORA está selada e 100% verificada.

---

## 17. Versão Final

`v0.7.1-final-foundation`

---

## 18. Declaração Obrigatória de Escopo

**`FASE 6 NÃO INICIADA`**

Nenhum crawler, scraper, embeddings, RAG, LLM ou integração de provedores cloud adicionais (Supabase, Cloudflare) foi implementado.

A fundação do **LÉXORA** está encerrada, auditada e selada, pronta para receber o Prompt oficial da Fase 6.
