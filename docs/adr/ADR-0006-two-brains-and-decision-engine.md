# ADR-0006: Separação Conceitual em Legal Brain, Fiscal Brain e Decision Engine

## Context
O ecossistema do LÉXORA precisa gerenciar simultaneamente a complexidade do conhecimento normativo-institucional (leis, decretos, acórdãos) e a complexidade operacional tributária (produtos, NCMs, CST, CFOP, alíquotas, cálculos).

## Problem
Evitar a mistura de responsabilidades onde o mecanismo de RAG jurídico decide enquadramentos fiscais ou onde o motor de cálculo tributário tenta interpretar normas jurídicas abstratas.

## Options
1. **Domínio Único Monolítico:** Tratar legislação e cálculos no mesmo módulo. (Gera alto acoplamento e imprecisão).
2. **Separação em Dois Cérebros + Orquestrador:** Divisão conceitual clara em `LEGAL BRAIN` (conhecimento jurídico), `FISCAL BRAIN` (regras e cálculos fiscais) e `DECISION ENGINE` (orquestrador de síntese e decisão).

## Decision
Adotar a divisão conceitual em 3 componentes:
- **`LEGAL BRAIN`:** Mantém a legislação oficial, atos normativos, grafo de relações, vigência temporal e evidências.
- **`FISCAL BRAIN`:** Mantém cadastro de produtos, NCM, CEST, CST, CSOSN, CFOP, regras operacionais e motor de cálculo determinístico.
- **`DECISION ENGINE`:** Componente de síntese que recebe as informações do *Legal Brain* e *Fiscal Brain* para produzir enquadramentos, justificativas, nível de confiança e ressalvas.

## Consequences
- Desacoplamento arquitetural completo entre a verdade jurídica e as regras operacionais da empresa.
- Facilidade em estender o sistema para novos ramos fiscais sem afetar a base jurídica global.

## Migration Strategy
Consolidado no modelo de dados e boundaries do projeto a partir da versão v0.2.0.
