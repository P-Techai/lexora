# ADR-0021: Catálogo Oficial de Conhecimento Fiscal e Processamento em Lote de NF-e

- **Status:** Aceito
- **Data:** 2026-08-14
- **Autores:** Equipe de Arquitetura LÉXORA

---

## 1. Contexto e Problema

Com a conclusão do motor operacional individual de NF-e na FASE 7, fez-se necessária a estruturação do catálogo oficial versionado de regras fiscais brasileiras e a expansão para processamento em lote de múltiplos arquivos XML com isolamento multi-tenant por empresa.

---

## 2. Decisão

1. **Catálogo Oficial Versionado (`FiscalRuleCatalog`):** Registro imutável de regras tributárias vinculadas obrigatoriamente a evidências jurídicas oficiais com hash SHA-256 (`content_hash`).
2. **Processamento em Lote Resiliente (`NFeBatchPipeline`):** Endpoint `POST /api/v1/fiscal/nfe/batch` com tratamento de falha por item e rastreamento de lote.
3. **Dez Cenários Golden Obliterantes:** Cobertura de classificação de produto, NCM temporal, CEST, ICMS-ST, DIFAL, FCP, Simples Nacional, ISS municipal, produtos ambíguos e regras conflitantes.
4. **Migration `0012_real_fiscal_knowledge_batch_nfe`:** Tabelas `fiscal_rule_catalog`, `fiscal_nfe_batches`, `fiscal_batch_items` com `ON DELETE RESTRICT`.
