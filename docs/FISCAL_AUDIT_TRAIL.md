# LÉXORA — Rastreabilidade e Audit Trail Fiscal (Fiscal Audit Trail)

Este documento especifica os mecanismos de auditoria cronológica, hashes determinísticos e reprcessamento fiscal no **LÉXORA (LXR)**.

---

# 1. Hashes Determinísticos SHA-256

Toda entidade no fluxo operacional carrega assinaturas criptográficas SHA-256 para auditoria:
- `decision_hash`: Assinatura dos dados de entrada, regras aplicadas, cálculos e status da decisão.
- `event_hash`: Assinatura imutável de transições no workflow de revisão humana.
- `override_hash`: Assinatura de modificações de override humano.

---

# 2. Reprocessamento & Fiscal Diff Engine

O endpoint `POST /api/v1/fiscal/decisions/{decision_id}/reprocess` permite reprocessar uma decisão histórica contra o motor atual e regras vigentes.
- **Resultado:** Produz uma NOVA decisão mantendo a antiga intacta.
- **Fiscal Diff:** `FiscalDiffEngine` gera um comparativo lado a lado identificando alterações de NCM, CST, CFOP, alíquota, base de cálculo, tributos e fundamentação jurídica.
