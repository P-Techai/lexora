# LÉXORA — Motor Fiscal Operacional (`OperationalFiscalEngine`)

Este documento especifica a operação do **Motor Fiscal Operacional** do **LÉXORA (LXR)** na **FASE 7**.

---

# 1. Visão Geral

O **Motor Fiscal Operacional** consolida a transformação do LÉXORA de uma fundação arquitetural para uma plataforma operacional completa capaz de processar documentos NF-e XML ponta a ponta:

```text
NF-e XML Payload
   ↓
XML Parsing & Defesa XXE (SecureNFeParser)
   ↓
Extração de Fatos Fiscais (FiscalFact)
   ↓
Identificação de Produto e Perfil Cadastral (FiscalProductProfile)
   ↓
Resolução Determinística de Regras Temporais (TaxRuleResolver)
   ↓
Apuracão e Cálculo de Tributos (ICMS, ICMS-ST, DIFAL, FCP, IPI, PIS, COFINS, ISS)
   ↓
Memória de Cálculo Auditável (CalculationMemory)
   ↓
Motor de Decisão (DecisionEngine & DecisionTrace)
   ↓
Fila de Revisão Humana (ReviewStateMachine se necessário)
```

---

# 2. Garantias de Não-Inferência

- **Custo Zero de Incerteza:** O LÉXORA NUNCA infere alíquotas ou tributos por aproximação de I.A. Inconsistências acionam `HUMAN REVIEW` / `REVIEW_REQUIRED`.
- **Diferenciação Fact vs Decision:** O XML informado é armazenado como `SOURCE FACT`. A apuração calculada pelo LÉXORA é gravada como `SYSTEM DECISION`.
