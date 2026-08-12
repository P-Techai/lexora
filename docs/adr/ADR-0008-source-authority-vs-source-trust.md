# ADR-0008: Separação Conceitual entre Autoridade da Fonte (Authority Level) e Confiabilidade Operacional (Trust Score)

## Context
Durante a Fase 1 e Fase 2, identificou-se a necessidade de diferenciar o nível de autoridade jurídica institucional de um órgão emissor da sua confiabilidade técnica ou disponibilidade operacional no momento da captura.

## Problem
Evitar a confusão entre o nível de autoridade hierárquico de uma fonte primária (ex.: Planalto vs. Secretaria Municipal) e a qualidade/disponibilidade do canal de comunicação no momento da captura.

## Options
1. **Utilizar apenas `authority_level` de 1 a 5:** Agrupava a importância institucional e a estabilidade técnica na mesma escala.
2. **Separação em Dois Atributos (`authority_level` e `trust_score`):**
   - `authority_level` (Inteiro de 1 a 5): Nível de autoridade institucional da fonte. (1: União/Planalto/DOU; 2: Órgãos Federais/STF/STJ/CARF; 3: Secretarias Estaduais; 4: Órgãos Municipais; 5: Portais comunitários/secundários).
   - `trust_score` (Float de 0.0 a 1.0): Confiabilidade técnica e integridade operacional do conector/portal no momento da ingestão.

## Decision
Adotar a separação conceitual explícita entre `authority_level` (autoridade institucional) e `trust_score` (confiabilidade operacional), registrando ambos no modelo de dados da entidade `Source`.

## Consequences
- Possibilidade de tratar uma fonte de alta autoridade (`authority_level=1`) cuja conexão estivesse instável (`trust_score=0.4`) sem alterar o status institucional da fonte.

## Migration Strategy
Implementado na versão v0.4.0-ingestion-contracts na entidade `Source`.
