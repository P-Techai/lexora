# LÉXORA — Especificação do Dashboard de Auditoria Fiscal (`FiscalAuditDashboard`)

Este documento especifica a interface web operacional e endpoints do **Audit Dashboard** do **LÉXORA (LXR)**.

---

# 1. Visão Geral

O **Audit Dashboard** expõe a camada operacional de visualização sobre o **Decision Engine** e **Fiscal Brain**:
- Visualização de fatos fiscais e classificação cadastral;
- Exibição de regras tributárias ativas e rejeitadas;
- Inspeção da memória de cálculo `Decimal` (`ROUND_HALF_UP`);
- Navegação visual na árvore de rastreabilidade Two-Brain (`DecisionTrace`);
- Fila de controle para revisão humana (`ReviewStatus`).

---

# 2. Endpoints Principais

- `GET /dashboard` (Web UI)
- `GET /api/v1/dashboard/summary` e `GET /api/v1/fiscal/dashboard/summary`
- `GET /api/v1/fiscal/decisions`
- `GET /api/v1/fiscal/decisions/{decision_id}`
- `GET /api/v1/fiscal/decisions/{decision_id}/trace`
- `GET /api/v1/fiscal/decisions/{decision_id}/calculations`
- `GET /api/v1/fiscal/decisions/{decision_id}/evidence`
- `GET /api/v1/fiscal/decisions/{decision_id}/report`
- `GET /api/v1/fiscal/decisions/{decision_id}/export`
