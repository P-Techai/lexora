# LÉXORA — Arquitetura do Cérebro Fiscal (Fiscal Brain Architecture)

Este documento descreve a arquitetura detalhada e governança do **Fiscal Brain** e **Decision Engine** do **LÉXORA (LXR)** na **FASE 6.3**.

---

# 1. Visão Geral da Arquitetura

O **Fiscal Brain** opera como o motor determinístico da plataforma LÉXORA. Ele é responsável por:
- Interpretar fatos fiscais de operações comerciais (`FiscalFact`);
- Classificar produtos, NCM, CST e CFOP de forma puramente determinística (`FiscalClassifier`);
- Avaliar a vigência de regras tributárias contra a data da operação (`TaxRuleEvaluator`);
- Executar cálculos tributários em precisão `Decimal` sem o uso de I.A./LLM ou floating point (`TaxCalculator`);
- Gerar árvores de execução e hashes auditáveis SHA-256 (`DecisionEngine` / `DecisionTrace`).

---

# 2. Desacoplamento Two-Brain

```text
LEGAL BRAIN (Autoridade Normativa)
   ├── Dispositivos Normativos (LegalNode)
   ├── Versões Normativas (LegalVersion)
   ├── Evidências Jurídicas (Evidence)
   └── Artefatos Brutos (RawArtifact)
          │
          │ (Porta de Aplicação: LegalRuleProvider)
          ▼
FISCAL BRAIN (Aplicação Determinística)
   ├── Perfil de Empresa (CompanyFiscalProfile)
   ├── Fatos Fiscais (FiscalFact)
   ├── Regras Fiscais Formalizadas (FiscalTaxRule)
   ├── Motor de Cálculo Decimal (TaxCalculator)
   └── Motor de Decisão (DecisionEngine)
          │
          ▼
   AUDIT LOG & MEMÓRIA IMUTÁVEL (PostgreSQL - ON DELETE RESTRICT)
```

---

# 3. Princípios de Segurança e Integridade

- **Zero LLM em Decisões Fiscais:** LLMs ou modelos probabilísticos são proibidos de calcular impostos ou inventar regras.
- **Temporabilidade Estrita:** A vigência da regra é avaliada contra `fact.operation_date`, impedindo o uso do relógio do sistema.
- **Idempotência Garantida:** Entradas idênticas produzem hashes SHA-256 idênticos para `decision_id` e `decision_hash`.
- **Imutabilidade Histórica:** Nenhum log de cálculo ou decisão é sobrescrito ou apagado do banco de dados.
