# ADR-0011: Resolução Dinâmica de Revogação por Data de Referência e Preservação da Imutabilidade Histórica

## Context
A revogação de uma norma jurídica é um evento no tempo que encerra sua eficácia a partir da data de revogação. Em auditorias jurídicas históricas, uma consulta feita para uma data $T$ anterior à revogação deve retornar a norma como `EFFECTIVE`, reproduzindo exatamente o estado histórico da época.

## Problem
Mutar estaticamente o campo `status` da tabela `legal_versions` para `REVOKED` no banco de dados destruiria o histórico, fazendo com que consultas para datas anteriores à revogação retornassem indevidamente `REVOKED`.

## Options
1. **Mutação Estática de Status (`version.status = REVOKED`):** Viola a reprodução histórica para datas $T < revocation\_date$.
2. **Resolução Dinâmica de Revogação por Data de Referência ($T$):**
   - Preserva os registros históricos originais intactos no banco de dados.
   - Encerra o período `effective_until = revocation_date` na versão e grava a relação `LegalRelationType.REVOKES` vinculada à `Evidence`.
   - O serviço `TemporalLegalSearchService` avalia se $T \ge revocation\_date$ para retornar `REVOKED` (com evidência), ou $T < revocation\_date$ para retornar `EFFECTIVE` (reprodução histórica perfeita).

## Decision
Adotar a Resolução Dinâmica de Revogação por Data de Referência $T$.

## Consequences
- 100% de imutabilidade histórica e reprodutibilidade de consultas jurídicas em qualquer momento do passado.

## Migration Strategy
Implementado no Gate de Auditoria v0.6.1-readiness-audit.
