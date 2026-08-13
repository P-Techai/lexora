# ADR-0015: Arquitetura de Recuperação Híbrida Jurídica (Hybrid Legal Retrieval)

## Context
Na Fase 6.1 do LÉXORA, construiu-se a primeira camada de recuperação jurídica híbrida sobre a fundação canônica selada. A recuperação deve unir a precisão da busca lexical (Full-Text Search) com a capacidade de generalização da busca vetorial semântica (embeddings), sem que vetores ou modelos de IA alterem ou substituam a Verdade Jurídica (Legal Truth).

## Decision
1. **Separação de Responsabilidades:** Legal Truth (Source $\to$ RawArtifact $\to$ Evidence $\to$ Version $\to$ Node) é mantida 100% imutável. A camada de Retrieval gera vetores de embedding e pontuações de busca sem alterar o fato jurídico.
2. **Contexto Hierárquico Canônico:** `CanonicalRetrievalTextBuilder` constrói o texto canônico de embedding incorporando os rótulos da hierarquia ancestral (`Norma > Livro > Título > Capítulo > Seção > Subseção > Artigo > Parágrafo > Inciso > Alínea > Item`).
3. **Reranking Determinístico:** A pontuação final combina scores lexicais, semânticos, autoridade da fonte e bônus de correspondência exata de identificador normativo (`final_score = 0.35 * lex + 0.35 * sem + 0.10 * auth + 0.20 * exact_bonus`).
4. **Filtragem Temporal Obrigatória:** Todas as consultas exigem uma data de referência $T$ e utilizam o `TemporalIntegrityValidator.is_date_in_range` para garantir que apenas normas vigentes em $T$ sejam retornadas.
5. **Cadeia de Proveniência em 5 Níveis:** Todo resultado de busca deve possuir os 5 elos de proveniência rastreáveis. Resultados com elos ausentes são descartados como não autoritativos.

## Consequences
- Capacidade de recuperação precisa e contextual de evidências normativas sem qualquer alucinação por LLM.
- **Status da Fase 6.1:** **`COMPLETE`**
- **Status da Fase 6.2:** **`AUTHORIZED`**
