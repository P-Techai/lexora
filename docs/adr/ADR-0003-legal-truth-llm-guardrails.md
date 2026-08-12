# ADR-0003: Princípio da Verdade Jurídica e Guardrails para LLMs

## Context
Modelos de Linguagem (LLMs) apresentam tendência a alucinações ao citar artigos, incisos, alíneas e vigências legislativas, o que é inaceitável em um sistema jurídico-fiscal profissional.

## Problem
Garantir que todas as afirmações jurídicas sejam 100% fundamentadas em legislação primária oficial e dispositivos normativos canônicos rastreáveis.

## Options
1. **Confiar na Resposta Gerada pelo LLM:** Utilizar respostas puras de modelos de linguagem. (Risco inaceitável de erro jurídico).
2. **LLM como Orquestrador + Base Normativa Canônica:** O LLM é restrito a funções de interpretação, extração e síntese, enquanto a verdade jurídica advém exclusivamente de nós normativos cadastrados e versionados (`LegalNode`).

## Decision
Adotar o Princípio da Verdade Jurídica:
- O LLM **NUNCA** é a fonte da verdade jurídica ou fiscal.
- Toda resposta jurídica DEVE explicitar norma, artigo, parágrafo, inciso, alínea, versão, vigência temporal e link para a fonte oficial primária.
- Estabelecimento da escala de confiabilidade: `CERTEZA`, `PROVÁVEL`, `INCERTA`, `CONFLITANTE`, `NÃO ENCONTRADA`.

## Consequences
- Garantia de auditabilidade total e eliminação de alucinações normativas.
- Respostas sem evidência documental suficiente são encaminhadas obrigatoriamente para Revisão Humana.

## Migration Strategy
Implementação contínua no pipeline do RAG Híbrido e no *Decision Engine*.
