# LÉXORA — Conhecimento Fiscal Oficial Real e Processamento em Lote (`Phase8RealFiscalKnowledge`)

Este documento especifica a integração de conhecimento fiscal real e o motor de processamento em lote de NF-e no **LÉXORA (LXR)** na **FASE 8**.

---

# 1. Visão Geral

A **FASE 8** conecta o motor determinístico do LÉXORA às fontes normativas oficiais brasileiras (Planalto, Receita Federal, CONFAZ e SEFAZs estaduais), introduzindo:
1. **Catálogo Oficial Versionado (`FiscalRuleCatalog`):** Regras temporalmente vigentes vinculadas a evidências jurídicas reais.
2. **Classificação Cadastral de Produtos (`ProductFiscalClassificationService`):** Definição determinística de NCM, CEST, CST, CSOSN e CFOP sem adivinhação por I.A.
3. **Processamento em Lote Resiliente (`POST /api/v1/fiscal/nfe/batch`):** Ingestão de múltiplos XMLs com tratamento de erros por item e acompanhamento de lote.
4. **Isolamento por Empresa (`company_id`):** Garantia de multi-tenancy e isolamento relacional e de aplicação.

---

# 2. Princípio da Evidência Oficial Soberana

Nenhuma alíquota ou classificação fiscal é aceita sem a devida evidência legal cadastrada (`FiscalRuleEvidence`). Aggregate comerciais ou palpites de LLM são terminantemente proibidos de gerar regras fiscais.
