# ADR-0018: Co-Pilot Fiscal, Dashboard de Auditoria e Workflow de Revisão Humana

- **Status:** Aceito
- **Data:** 2026-08-14
- **Autores:** Equipe de Arquitetura LÉXORA

---

## 1. Contexto e Problema

Com os motores **Legal Brain**, **Fiscal Brain** e **Decision Engine** concluídos na FASE 6.3, fez-se necessária a criação de uma superfície operacional interativa para que usuários humanos possam:
1. Auditar decisões tributárias e visualizar a memória de cálculo completa;
2. Navegar pela cadeia de proveniência legal;
3. Interagir com uma fila de revisão humana controlada;
4. Consultar explicações determinísticas via Co-Pilot sem comprometer a autoridade do motor.

---

## 2. Decisão

1. **Implementação do Fiscal Co-Pilot (`LLM = EXPLANATION ONLY`):** O Co-Pilot é estritamente explicativo. O resultado do motor tributário é mantido soberano.
2. **Máquina de Estados de Revisão Humana:** Transições estritas (`OPEN` -> `IN_REVIEW` -> `APPROVED` / `REJECTED` / `ESCALATED`) com eventos imutáveis append-only (`ReviewEvent`).
3. **Preservação de Decisões Históricas:** Nenhuma decisão ou cálculo é modificado ou apagado via `DELETE`. Intervenções humanas utilizam `HumanOverride` que mantém a decisão original intacta.
4. **Dashboard Portável e Servido pelo FastAPI:** Endpoint `/dashboard` em HTML/JS responsivo e moderno sem acoplamento a frameworks frontend externos.
5. **Reprocessamento com Fiscal Diff:** Endpoint `/reprocess` gera nova execução e comparativo diff.

---

## 3. Consequências

- **Auditabilidade Total:** 100% das decisões, revisões e overrides são rastreáveis via hashes SHA-256.
- **Inviolabilidade do Domínio Fiscal:** Interfaces web e assistentes de I.A. não possuem autoridade para alterar diretamente o resultado do motor sem rastro de auditoria.
