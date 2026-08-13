# LÉXORA — Conjunto de Dados Piloto da FASE 5 (Phase 5 Pilot Dataset)

Este documento registra o dataset oficial selecionado para a primeira ingestão controlada e auditada no **LÉXORA (LXR)**.

---

# 1. Documentos Selecionados para Ingestão Piloto

| ID do Piloto | Tipo Normativo | Número / Identificador | Descrição do Ato | Fonte Oficial |
| :--- | :--- | :--- | :--- | :--- |
| **PILOT-01** | **Constituição Federal** | CF/1988 (Fragmento Título I/II) | Constituição da República Federativa do Brasil | Planalto (`planalto.gov.br`) |
| **PILOT-02** | **Lei Complementar** | LC 116/2003 | Imposto Sobre Serviços (ISS) | Planalto (`planalto.gov.br`) |
| **PILOT-03** | **Lei Ordinária** | Lei 10.406/2002 (Fragmento) | Código Civil Brasileiro | Planalto (`planalto.gov.br`) |
| **PILOT-04** | **Decreto Regulamentar** | Decreto 9.580/2018 (Fragmento) | Regulamento do Imposto de Renda (RIR) | Planalto (`planalto.gov.br`) |

---

# 2. Expectativas de Ingestão e Golden Tests

- Todos os documentos possuem `dry_run=True` prévio para diagnóstico sem persistência.
- O parser estrutural reconhece os nós fundamentais e grava as evidências de proveniência vinculadas às URLs oficiais de origem.
