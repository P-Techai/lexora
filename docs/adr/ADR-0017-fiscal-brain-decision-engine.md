# ADR-0017: Arquitetura do Cérebro Fiscal (Fiscal Brain) e Motor de Decisão (Decision Engine)

## Context
Na Fase 6.3 do LÉXORA, implementou-se o subsistema **Fiscal Brain** e o **Decision Engine** para automação de classificações e cálculos tributários brasileiros (ICMS, IPI, PIS, COFINS, ISS, CBS, IBS, IS) com rastreabilidade total até a base normativa do **Legal Brain**.

## Decision
1. **Zero LLM em Decisões Fiscais:** Proibir que LLMs tomem ou alterem decisões tributárias, alíquotas, bases de cálculo ou classificações fiscais. Todas as operações fiscais são efetuadas por código determinístico em Python.
2. **Matemática Decimal:** Utilizar exclusivamente a classe `Decimal` para cálculos e arredondamentos (`TaxRoundingService`).
3. **Avaliação Temporal pela Data da Operação:** Regras tributárias são avaliadas contra `fact.operation_date`, impedindo o uso de `datetime.now()` ou `date.today()`.
4. **Governança Two-Brain:** Manter o Legal Brain como autoridade normativa e o Fiscal Brain como aplicador de regras formalizadas via porta `LegalRuleProvider`.
5. **Imutabilidade Auditável no Banco:** Tabelas fiscais utilizam `ON DELETE RESTRICT` nas FKs, impedindo a destruição de proveniência histórica.

## Consequences
- 100% de determinismo e reprodutibilidade nas decisões tributárias.
- Rastreabilidade ponto a ponto (Fato -> Regra -> Cálculo -> Dispositivo Legal -> Evidência).
- Conformidade total com a Lei Geral de Proteção de Dados e exigências de auditoria fiscal.
