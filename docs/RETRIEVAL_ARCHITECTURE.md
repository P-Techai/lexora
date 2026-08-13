# LÉXORA — Arquitetura de Recuperação Híbrida Jurídica (Retrieval Architecture)

Este documento especifica a arquitetura da camada de busca e recuperação jurídica híbrida do **LÉXORA (LXR)** implementada na **FASE 6.1**.

---

# 1. Pipeline de Recuperação de 7 Estágios

```text
QUERY DE BUSCA + DATA DE REFERÊNCIA (T)
      ↓
1. NORMALIZAÇÃO DE QUERY (LegalQueryNormalizer)
      ↓
2. BUSCA LEXICAL (PostgreSQL Full-Text Search)  +  3. BUSCA VETORIAL (pgvector / Cosine)
      └───────────────────────┬────────────────────────┘
                              ↓
4. MERGE & DEDUPLICAÇÃO DE CANDIDATOS
                              ↓
5. RERANKING DETERMINÍSTICO (Lexical + Semantic + Authority + Exact Bonus)
                              ↓
6. FILTRAGEM TEMPORAL DE VIGÊNCIA (TemporalIntegrityValidator.is_date_in_range(T))
                              ↓
7. VALIDAÇÃO DE PROVENIÊNCIA EM 5 NÍVEIS (Node -> Version -> Evidence -> Artifact -> Source)
                              ↓
LEGAL RETRIEVAL RESULT (LegalRetrievalResultResponse)
```

---

# 2. Fórmula de Reranking Híbrido

A pontuação final $S_{final}$ de cada dispositivo candidato é calculada por:

$$S_{final} = 0.35 \cdot S_{lexical} + 0.35 \cdot S_{semantic} + 0.10 \cdot S_{authority} + 0.20 \cdot S_{exact\_bonus}$$

- $S_{lexical}$: Pontuação de correspondência de termos no texto normalizado.
- $S_{semantic}$: Similaridade de cosseno vetorial.
- $S_{authority}$: Nível de autoridade da fonte oficial (1 a 5, normalizado para 0.2 a 1.0).
- $S_{exact\_bonus}$: Bônus de 0.3 se o número do artigo ou da norma bate exatamente com a query.
