# LÉXORA — Operational Tax Workbench & User Flow (`Phase9Workbench`)

Este documento especifica a arquitetura do **Operational Tax Workbench** do **LÉXORA (LXR)** na **FASE 9**.

---

# 1. Visão Geral do Fluxo End-to-End

```text
COMPANY → FISCAL PROFILE → XML NF-e → VALIDATION → PRODUCT CLASSIFICATION → FISCAL RULE RESOLUTION → TAX CALCULATION → HUMAN REVIEW WHEN REQUIRED → DECISION → AUDIT TRACE → REPORT
```

---

# 2. Transições Formais de Estado

### Estados de NF-e (`nfe_state`):
- `RECEIVED`: Payload recebido.
- `VALIDATED`: Parsing e validação de schema / XXE ok.
- `PROCESSING`: Avaliação de regras e apuração de tributos.
- `PROCESSED`: Apuração completa sem pendências.
- `VALIDATION_FAILED`: Falha no schema ou perfil fiscal expirado.
- `HUMAN_REVIEW`: Exige revisão por ambiguidade ou regra ausente.
- `FAILED`: Erro fatal de processamento.

### Estados de Produto (`product_state`):
- `UNCLASSIFIED`: Produto não classificado.
- `CLASSIFIED`: NCM, CEST, CST e CFOP determinados.
- `HUMAN_REVIEW`: Produto ambíguo ou sem regra oficial.

### Estados da Decisão (`decision_state`):
- `PROPOSED`: Decisão calculada proposta.
- `CONFIRMED`: Decisão confirmada pelo sistema ou revisor.
- `HUMAN_REVIEW`: Pendente de ação na fila de revisão.
