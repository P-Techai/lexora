# LÉXORA — Workflow de Revisão Humana (Human Review Workflow)

Este documento especifica a máquina de estados determinística e a auditoria de revisões humanas no **LÉXORA (LXR)** na **FASE 6.4**.

---

# 1. Máquina de Estados Determinística

```text
       OPEN
        │
        ▼
    IN_REVIEW
   /    |    \
  /     |     \
 ▼      ▼      ▼
APPROVED REJECTED ESCALATED
```

- **Transições Permitidas:**
  - `OPEN` → `IN_REVIEW` (início da análise)
  - `IN_REVIEW` → `APPROVED` (aprovado pelo revisor humano)
  - `IN_REVIEW` → `REJECTED` (rejeitado pelo revisor humano)
  - `IN_REVIEW` → `ESCALATED` (escalado para comitê legal/fiscal)

---

# 2. Imutabilidade e Overrides

- **Preservação da Decisão Original:** A intervenção humana NUNCA apaga ou altera a `TaxDecision` original.
- **Eventos Append-Only (`ReviewEvent`):** Cada transição gera um registro de evento imutável no PostgreSQL com hash SHA-256 (`event_hash`).
- **Human Overrides (`HumanOverride`):** Quando um override ocorre, o sistema gera uma nova decisão vinculada à decisão original mantida intacta.
