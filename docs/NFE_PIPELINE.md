# LÉXORA — Pipeline de Processamento de NF-e (NF-e Pipeline)

Este documento descreve o fluxo de ingestão e análise determinística de NF-e no **LÉXORA (LXR)** na **FASE 7**.

---

# 1. Fluxo de Ingestão e Análise (`POST /api/v1/fiscal/nfe/analyze`)

1. **Recepção:** Recebe o payload UTF-8 do XML da NF-e, o ID da empresa (`company_id`) e a data de referência (`reference_date`).
2. **Parsing Seguro:** Invocação do `SecureNFeParser` com verificação de limites (máx. 10MB) e desativação de entidades externas (XXE).
3. **Extração de Fatos Fiscais:** Converte os dados do XML em `FiscalFact`. Preserva tributos, CST e CFOP originais como `SOURCE FACT`.
4. **Avaliação Determinística:** Executa o `DecisionEngine` para apurar tributos e determinar CST/CFOP calculados como `SYSTEM DECISION`.
5. **Apuracão e Retorno:** Gera memória de cálculo, hash SHA-256 da análise e encaminha itens ambíguos para revisão humana.
