# ADR-0010: Semântica Temporal de Intervalos Semi-Abertos, Auditabilidade de Conflitos e Revogação Imutável

## Context
A determinação da Verdade Jurídica em sistemas tributários exige que o tempo seja tratado como uma dimensão estrutural primária e auditável, eliminando incertezas em limites de vigência ou em processos de revogação.

## Problem
Evitar a perda de histórico decorrente de exclusões físicas (`DELETE` SQL), evitar a resolução silenciosa de conflitos de vigência por IAs ou heurísticas não auditáveis e resolver ambiguidades de fronteira entre versões consecutivas.

## Options
1. **Modelos de Datas Fechadas $[A, B]$:** Cria ambiguidades no dia do limite $B$ entre versões consecutivas.
2. **Resolução Silenciosa de Conflitos (Escolher a versão mais recente):** Viola a auditabilidade jurídica.
3. **Intervalo Semi-Aberto $[effective\_from, effective\_until)$ + Revogação por Evento + Conflito Não-Silencioso:**
   - Adota a convenção matemática semi-aberta $[effective\_from, effective\_until)$.
   - Registra o status `TEMPORAL_CONFLICT` em caso de sobreposição sem resolvê-lo arbitrariamente.
   - Proíbe comandos `DELETE` SQL para revogações, tratando a revogação como evento que encerra o `effective_until` e exige `Evidence`.

## Decision
Adotar o modelo de Intervalo Semi-Aberto $[effective\_from, effective\_until)$, auditabilidade estrita de conflitos e revogação imutável com proveniência.

## Consequences
- Total auditabilidade histórica e determinismo nas consultas temporais em qualquer data de referência $T$.

## Migration Strategy
Implementado na versão v0.6.0-temporal-truth.
