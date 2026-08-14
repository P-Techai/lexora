# LÉXORA — Reprocessamento Histórico Fiscal (Fiscal Reprocessing)

Este documento especifica os mecanismos de reprocessamento sem alteração destrutiva do **LÉXORA (LXR)** na **FASE 6.5**.

---

# 1. Princípio da Imutabilidade Histórica

Quando novas regras tributárias são promulgadas ou versões de motor evoluem:
- As decisões históricas passadas PERMANECEM 100% INTACTAS no banco de dados.
- O reprocessamento gera um registro `ReprocessingRun` vinculando a decisão antiga (`source_decision_id`) à nova decisão (`new_decision_id`).
- O comparativo `FiscalDiffEngine` expõe as divergências de alíquotas, bases, impostos e regras aplicadas.
