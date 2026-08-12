# LÉXORA — Especificação de Integridade Jurídica (Legal Integrity Specification)

Este documento estabelece as regras de validação estrutural da árvore normativa e proveniente de evidências no **LÉXORA (LXR)**.

---

# 1. Regras de Integridade da Árvore Hierárquica (`LegalTreeIntegrityValidator`)

Para que uma lista de nós (`LegalNode`) seja considerada uma árvore válida:

1. **Pertencimento Único de Versão:** Todos os nós da árvore devem possuir obrigatoriamente o mesmo `legal_version_id`.
2. **Proibição Absoluta de Ciclos:** Um nó jamais pode ser ancestral de si mesmo ($A \rightarrow B \rightarrow C \rightarrow A$). A presença de ciclo dispara `TreeCycleDetectedError`.
3. **Consistência de Posição Ordinal (`position`):** Todos os nós sob o mesmo nó pai (`parent_id`) devem ter posições ordinais positivas ($1, 2, 3...$) estritamente únicas. Posições duplicadas disparam `InconsistentPositionError`.
4. **Caminho Determinístico (`path`):** O campo `path` de cada nó deve ser gerado pelo `LegalNodePathBuilder` (ex: `/art-001/par-001/inc-001`).

---

# 2. Proviniência Exigida em Relações Normativas

- Relações dos tipos `AMENDS` (alteração de redação) e `REVOKES` (revogação) exigem obrigatoriamente a associação de um `evidence_id` válido.
- Tentar criar uma relação de alteração/revogação sem evidência spara a exceção `MissingEvidenceError`.

---

# 3. Tratamento de Exceções de Domínio

- `InvalidLegalDocumentError`: Metadados ou origem inválidos.
- `InvalidEffectivePeriodError`: `effective_until < effective_from`.
- `DuplicateLegalDocumentError`: Rejeição de duplicatas sem versão.
- `MissingEvidenceError`: Falta de evidência documental em alterações.
- `TreeCycleDetectedError`: Rejeição de ciclos hierárquicos.
- `InconsistentPositionError`: Rejeição de posições ordinais duplicadas no mesmo nível.
