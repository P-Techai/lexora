# LÉXORA — Gestão de Divergências Fiscais (Divergence Management)

Este documento especifica o motor de divergências tributárias e a classificação determinística de severidade do **LÉXORA (LXR)** na **FASE 6.4**.

---

# 1. Objeto Divergência (`Divergence`)

Uma divergência é gerada deterministicamente pelo `DivergenceEngine` quando:
1. Houver conflito normativo entre regras ativas de mesma prioridade (`DecisionStatus.CONFLICT`);
2. Houver ausência de fundamentação jurídica ou evidência (`DecisionStatus.LEGAL_BASIS_MISSING`);
3. O valor do tributo calculado diferir do valor esperado em integrações fiscais.

---

# 2. Classificação de Severidade

- **INFO:** Inconsistências informativas sem impacto financeiro ou fiscal direto.
- **WARNING:** Divergências de cálculo financeiro de menor valor (ex.: < R$ 50.00).
- **CRITICAL:** Conflitos de regras tributárias, ausência de fundamentação jurídica, inconsistência temporal ou divergências materiais de valores tributários.
- **Regra Soberana:** A severidade é calculada deterministicamente. NUNCA utilizar LLMs para decidir severidade.
