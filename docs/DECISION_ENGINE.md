# LÉXORA — Especificação do Motor de Decisão (Decision Engine)

Este documento especifica a arquitetura e fluxo de execução do **Decision Engine** do **LÉXORA (LXR)** implementados na **FASE 6.3**.

---

# 1. Fluxo Determinístico Two-Brain

```text
FATO FISCAL (FiscalFact)
    ↓
NORMALIZAÇÃO (FiscalNormalizer)
    ↓
CLASSIFICAÇÃO (FiscalClassifier)
    ↓
BUSCA DE REGRAS NA DATA DA OPERAÇÃO (TaxRuleEvaluator)
    ↓
CONSULTA DA BASE LEGAL NORMATIVA (Legal Brain)
    ↓
CÁLCULO TRIBUTÁRIO DECIMAL (TaxCalculator)
    ↓
GERAÇÃO DA ÁRVORE DE DECISÃO (DecisionTrace)
    ↓
HASHES SHA-256 IMUTÁVEIS (decision_hash, input_hash, calc_hash)
    ↓
DECISÃO FINAL (APPROVED / REVIEW_REQUIRED / CONFLICT / NO_APPLICABLE_RULE)
```

---

# 2. Status de Decisão

- `APPROVED`: Fato fiscal classificado, regras ativas com fundamentação legal confirmada e cálculos calculados sem conflitos.
- `REVIEW_REQUIRED`: NCM duvidoso, ausência de evidência normativa vinculada ou ambiguidade cadastral.
- `CONFLICT`: Múltiplas regras com a mesma prioridade e jurisdição apresentando alíquotas ou condições divergentes.
- `NO_APPLICABLE_RULE`: Nenhuma regra ativa aplicável na data de referência da operação.
- `INSUFFICIENT_DATA`: Dados obrigatórios ausentes para avaliação.

---

# 3. Auditabilidade e Reprodutibilidade

Toda decisão gera:
- `decision_id`: Identificador determinístico SHA-256 derivado dos dados de entrada, regras e resultados.
- `decision_trace`: Estrutura JSON auditável contendo todas as etapas percorridas pelo motor.
- `decision_hash`: Assinatura SHA-256 garantindo reprodutibilidade idêntica a qualquer tempo.
