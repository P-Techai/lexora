# LÉXORA — Proveniência e Vínculo Jurídico Fiscal (Fiscal Provenance)

Este documento especifica a cadeia de proveniência de regras fiscais e decisões no **LÉXORA (LXR)**.

---

# 1. Cadeia Completa de Proveniência

Toda decisão fiscal (`TaxDecision` / `Decision`) possui uma cadeia ininterrupta de proveniência rastreável até a legislação brasileira oficial:

```text
TaxDecision / Decision
   ↓
FiscalTaxRule
   ↓
LegalNode (Artigo / Inciso / Parágrafo)
   ↓
LegalVersion (Versão Normativa)
   ↓
Evidence (Evidência Auditada)
   ↓
RawArtifact (Artefato Bruto Oficial)
   ↓
Source (Fonte Oficial / Diário Oficial / Planalto)
```

---

# 2. Rejeição de Regras Órfãs

Se uma regra fiscal em status `ACTIVE` não contiver `source_legal_node_id`, `source_legal_version_id` e `evidence_id`, o **Decision Engine** atribui o status `LEGAL_BASIS_MISSING` / `REVIEW_REQUIRED`. Decisões fiscais sem fundamentação não podem afirmar certeza.
