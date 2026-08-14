# LÉXORA — Especificação do Dashboard de Auditoria (Audit Dashboard)

Este documento especifica a interface web operacional e endpoints de auditoria do **LÉXORA (LXR)** implementados na **FASE 6.4**.

---

# 1. Interface Web Portável (`/dashboard`)

A interface web é servida diretamente pelo FastAPI (`HTMLResponse`), sem acoplamento a frameworks pesados de frontend.

### Recursos:
- **Painel de Métricas:** Exibe total de decisões, decisões aprovadas, revisões exigidas e conflitos normativos em tempo real.
- **Tabela de Decisões Recentes:** Lista decisões com visualização de status, NCM, data da operação e botão de explicação interativa.
- **Visualizador de Árvore de Decisão (`DecisionTrace`):** Exibe as etapas (`INPUT` -> `NORMALIZATION` -> `CLASSIFICATION` -> `RULE DISCOVERY` -> `CALCULATION` -> `DECISION`).
- **Fiscal Co-Pilot Panel:** Painel interativo para geração de explicações determinísticas.

---

# 2. Endpoints de Dashboard

- `GET /api/v1/dashboard/summary`
- `GET /api/v1/fiscal/decisions`
- `GET /api/v1/fiscal/decisions/{decision_id}`
- `GET /api/v1/fiscal/decisions/{decision_id}/trace`
- `GET /api/v1/fiscal/decisions/{decision_id}/calculations`
- `GET /api/v1/fiscal/decisions/{decision_id}/evidence`
