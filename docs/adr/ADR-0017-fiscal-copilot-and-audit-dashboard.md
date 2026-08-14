# ADR-0017: Co-Pilot Fiscal, Dashboard de Auditoria e Workflow de Revisão Humana

- **Status:** Aceito
- **Data:** 2026-08-14
- **Autores:** Equipe de Arquitetura LÉXORA

---

## 1. Contexto e Problema

Com os motores **Legal Brain**, **Fiscal Brain** e **Decision Engine** concluídos na FASE 6.3, fez-se necessária a criação de uma superfície operacional interativa para que usuários humanos possam auditar decisões tributárias, visualizar a memória de cálculo completa, navegar pela cadeia de proveniência legal e interagir com uma fila de revisão humana controlada.

---

## 2. Decisão

1. **Implementação do Fiscal Co-Pilot (`LLM = EXPLANATION ONLY`):** O Co-Pilot é estritamente explicativo. O resultado do motor tributário é mantido soberano.
2. **Máquina de Estados de Revisão Humana:** Transições estritas (`OPEN` -> `IN_REVIEW` -> `APPROVED` / `REJECTED` / `ESCALATED`) com eventos imutáveis append-only (`ReviewEvent`).
3. **Preservação de Decisões Históricas:** Nenhuma decisão ou cálculo é modificado ou apagado via `DELETE`.
4. **Dashboard Portável e Servido pelo FastAPI:** Endpoint `/dashboard` em HTML/JS responsivo.
5. **Reprocessamento com Fiscal Diff:** Endpoint `/reprocess` gera nova execução e comparativo diff.
