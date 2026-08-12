# LÉXORA — Especificação de Hardening de Integridade Jurídica (Legal Integrity Hardening)

Este documento detalha o conjunto de correções e proteções aplicadas na versão **`v0.6.3-final-integrity-closure`** para garantir a inviolabilidade da cadeia de Verdade Jurídica do **LÉXORA (LXR)**.

---

# 1. Eliminação de Cascades e Set Null Destrutivos (`ON DELETE RESTRICT`)

Nenhuma entidade da cadeia relacional jurídica ou de proveniência pode possuir `ON DELETE CASCADE` ou `ON DELETE SET NULL`. Todas as chaves estrangeiras foram ajustadas para `RESTRICT` tanto nos modelos ORM (`src/infrastructure/db/models/`) quanto nas migrations de banco `0003_legal_integrity_hardening.py` e `0004_evidence_fk_integrity.py`.

- `legal_versions.legal_document_id` $\to$ `ON DELETE RESTRICT`
- `legal_nodes.legal_version_id` $\to$ `ON DELETE RESTRICT`
- `legal_nodes.parent_id` $\to$ `ON DELETE RESTRICT`
- `legal_relations.source_node_id` $\to$ `ON DELETE RESTRICT`
- `legal_relations.target_node_id` $\to$ `ON DELETE RESTRICT`
- `evidences.legal_document_id` $\to$ `ON DELETE RESTRICT`
- `evidences.legal_version_id` $\to$ `ON DELETE RESTRICT`
- `evidences.legal_node_id` $\to$ `ON DELETE RESTRICT`

---

# 2. Fonte Única de Verdade para a Matemática Temporal

A função `TemporalIntegrityValidator.is_date_in_range(target_date, effective_from, effective_until)` $[effective\_from, effective\_until)$ é a única implementação da matemática temporal do sistema:
- `LegalVersion.is_effective_on()` delega para essa função.
- `TemporalLegalSearchService` delega para essa função.
- Limite no término ($T == effective\_until$) é estritamente exclusivo (`NOT EFFECTIVE`).

---

# 3. Proibição de Auto-Relações de Revogação

Uma norma não pode criar uma relação `DOCUMENTO A REVOKES DOCUMENTO A` para representar sua própria revogação. Se a revogação não possuir um nó/ato revogador distinto (`revoking_node_id`), os casos de uso `RevokeLegalDocumentUseCase` e `RevokeLegalNodeUseCase` disparam `MissingRevokingSourceError` sem inventar uma auto-relação.

---

# 4. Esclarecimento Terminológico: Temporal Closure vs. Physical Immutability

O encerramento do período de vigência de uma versão histórica (`effective_until = revocation_date`) é classificado como **Temporal Closure / Version Lifecycle**. Ele não destrói fatos históricos e garante que consultas para datas $T < revocation\_date$ continuem retornando o estado histórico prévio intacto.

---

# 5. Downgrade Determinístico em Migrations

Todas as migrations do Alembic (`0001`, `0002`, `0003`, `0004`) possuem métodos `upgrade()` e `downgrade()` completos e determinísticos, sem o uso de `pass` evasivo.

---

# 6. Status das Infraestruturas em Nuvem

- **Neon PostgreSQL:** NÃO INTEGRADO (Provisionado para fase futura).
- **Supabase Storage/DB:** NÃO INTEGRADO (Provisionado para fase futura).
- **Cloudflare R2/Workers:** NÃO INTEGRADO (Provisionado para fase futura).
