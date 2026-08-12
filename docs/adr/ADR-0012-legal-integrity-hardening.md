# ADR-0012: Hardening de Integridade Jurídica, Eliminação de Cascades Destrutivos e Proibição de Auto-Revogação

## Context
Após auditoria arquitetural independente (Prompt 06.1), identificou-se a necessidade de eliminar qualquer risco de destruição de dados históricos por cascata relacional, unificar a matemática temporal em uma única fonte de verdade dominial e proibir relações de revogação auto-referenciadas.

## Problem
1. Existência de `ON DELETE CASCADE` em modelos relacionais e migrations anteriores, com risco de exclusão acidental de histórico normativo.
2. Risco de auto-relação `DOCUMENTO A REVOKES DOCUMENTO A` se um nó revogador não fosse informado.
3. Necessidade de formalizar a terminologia de "Temporal Closure / Version Lifecycle" em contraste com "Physical Immutability".

## Decision
1. **Proibição Absoluta de Cascade Destrutivo:** Todas as chaves estrangeiras da cadeia jurídica (`legal_documents`, `legal_versions`, `legal_nodes`, `legal_relations`, `evidences`, `sources`, `raw_artifacts`, `acquisition_audit_logs`) adotam estritamente `ON DELETE RESTRICT` (ORM e Migration `0003_legal_integrity_hardening`).
2. **Fonte Única de Verdade Temporal:** A função `TemporalIntegrityValidator.is_date_in_range(target_date, effective_from, effective_until)` $[effective\_from, effective\_until)$ é a única implementação da matemática temporal, utilizada por `LegalVersion.is_effective_on` e `TemporalLegalSearchService`.
3. **Proibição de Auto-Revogação:** As revogações exigem obrigatoriamente um nó/ato revogador distinto. A tentativa de criar uma relação de revogação sem origem válida dispara `MissingRevokingSourceError`.
4. **Esclarecimento Terminológico:** O encerramento da vigência (`effective_until = revocation_date`) é denominado **Temporal Closure / Version Lifecycle**, garantindo 100% de integridade histórica e reprodutibilidade de consultas em qualquer momento do passado.
5. **Declaração de Infraestrutura Cloud:** Neon, Supabase e Cloudflare permanecem provisionados mas **NÃO INTEGRADOS** nesta fase.

## Consequences
- Garantia de que nenhuma exclusão no banco poderá destruir a cadeia de verdade jurídica.
- Reconstrução histórica determinística em qualquer data $T$.

## Migration Strategy
Consolidado na versão v0.6.2-legal-integrity-hardening via Migration 0003.
