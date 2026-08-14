# ADR-0020: Motor Fiscal Operacional e Pipeline de NF-e End-to-End

- **Status:** Aceito
- **Data:** 2026-08-14
- **Autores:** Equipe de Arquitetura LÉXORA

---

## 1. Contexto e Problema

Com a classificação de produtos e a infraestrutura de cálculo tributário finalizadas na FASE 6.5, tornou-se necessária a implementação do fluxo fiscal operacional End-to-End capaz de ingerir payloads XML de NF-e, realizar extração determinística e aplicar apurações de impostos completas.

---

## 2. Decisão

1. **Separação Fato do XML vs Decisão do Sistema:** Preservação estrita dos tributos, CST e CFOP informados no XML como `SOURCE FACT`, sem sobrescrever os valores calculados pelo sistema (`SYSTEM DECISION`).
2. **Defesa Incondicional Contra XXE:** O parser XML opera com entidades desativadas e limite rígido de payload de 10MB.
3. **Idempotência por Hash do XML:** Garantia de idempotência utilizando a chave de acesso da NF-e e o hash SHA-256 do conteúdo bruto.
4. **Cinco Cenários Golden Obliterantes:** Validação de fluxos internos, interestaduais, regras temporais de 2024 vs 2025, casos ambíguos e conflitos normativos.
5. **Migration `0011_nfe_operational_fiscal_engine`:** Criação da tabela `fiscal_nfe_analyses` com proteção relacional `ON DELETE RESTRICT`.
