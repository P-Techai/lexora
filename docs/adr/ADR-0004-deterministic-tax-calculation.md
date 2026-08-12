# ADR-0004: Motor de Cálculo Tributário Determinístico Auditável

## Context
Cálculos de tributos (ICMS, PIS, COFINS, ISS, IPI, CBS, IBS, IS) exigem exatidão matemática, aplicação estrita de alíquotas e conformidade legal vinculante.

## Problem
Evitar imprecisões aritméticas de ponto flutuante ou alucinações de modelos de IA em valores de impostos.

## Options
1. **Delegar Cálculos a Prompts de LLM:** Inviável e impreciso.
2. **Motor de Cálculo Determinístico Puro em Python:** Execução aritmética em código Python utilizando o tipo `Decimal` (NBR 5891) e registro auditável de memória de cálculo (`TaxMemoryLog`).

## Decision
Implementar um Motor de Cálculo Determinístico puro:
- Proibição absoluta de uso de LLMs para executar cálculos financeiros.
- Toda operação gera um registro imutável `TaxMemoryLog` contendo entradas, fórmula aplicada, versão da regra, resultado e fundamento legal.

## Consequences
- Cálculo 100% auditável, reprodutível e livre de erros de arredondamento.

## Migration Strategy
Mantido como núcleo do *Fiscal Brain*.
