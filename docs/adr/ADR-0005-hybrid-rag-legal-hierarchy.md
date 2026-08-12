# ADR-0005: RAG Híbrido com Reordenamento por Hierarquia Jurídica

## Context
A legislação brasileira possui particularidades estruturais complexas como hierarquia de normas (Constituição > LC > LO > Decreto > IN), vigência temporal e revogações implícitas/explícitas.

## Problem
Evitar a recuperação de artigos revogados ou desatualizados e garantir a busca precisa por números de artigos, NCMs ou conceitos semânticos.

## Options
1. **Busca Vetorial Simples (Similarity Search):** Insuficiente para números de leis ou termos numéricos exatos.
2. **Retrieval Híbrido (BM25 + pgvector + Filtro Temporal + Legal Reranker):** Combinação de busca lexical e vetorial com filtro temporal por data da operação fiscal e reordenamento por hierarquia jurídica.

## Decision
Adotar o pipeline de RAG Híbrido com 4 etapas:
1. Busca Lexical (BM25) para correspondências numéricas exatas;
2. Busca Vetorial (`pgvector`) para simetria semântica;
3. Filtro Temporal estrito (`effective_from <= date <= effective_until`);
4. Reordenador Jurídico (*Legal Reranker*) respeitando a hierarquia de normas.

## Consequences
- Respostas normativas precisas e imunes a normas desatualizadas.

## Migration Strategy
Será implementado na Fase 5 do Roadmap.
