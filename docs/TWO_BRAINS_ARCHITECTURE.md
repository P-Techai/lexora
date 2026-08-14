# LÉXORA — Arquitetura dos 2 Cérebros (Two-Brain Architecture)

Este documento descreve a coexistência governada e desacoplada dos dois subsistemas do **LÉXORA (LXR)**: **Legal Brain** e **Fiscal Brain**.

---

# 1. Divisão de Responsabilidades

| Princípio | Legal Brain | Fiscal Brain |
| :--- | :--- | :--- |
| **Papel** | Autoridade Normativa e Verdade Legal Canônica | Aplicação de Regras Fiscais e Cálculos |
| **Fonte de Verdade** | Legislação Brasileira Oficial, Atos Normativos, Versões e Evidências | Regras Tributárias Estruturadas Parametrizadas |
| **Execução** | Temporalidade Legal, Hierarquia Normativa, FTS, Hybrid RAG | Cálculo Decimal, Classificação NCM/CST/CFOP, Motor de Decisão |
| **I.A. / LLM** | Auxilia em síntese e retrieval contextual com guardrails estritos | **ESTRITAMENTE ZERO LLM** (100% determinístico por código) |

---

# 2. Protocolo de Comunicação via Ports

O **Fiscal Brain** nunca acessa diretamente as tabelas normativas do **Legal Brain**. Toda consulta à legislação é efetuada através da porta de aplicação `LegalRuleProvider`.
