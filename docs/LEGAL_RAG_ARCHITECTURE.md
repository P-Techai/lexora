# LÉXORA — Arquitetura de RAG Jurídico Contextual (Legal RAG Architecture)

Este documento especifica a arquitetura da camada de síntese e geração de respostas jurídicas baseada em evidências do **LÉXORA (LXR)** implementada na **FASE 6.2**.

---

# 1. Diagrama de Pipeline de 11 Estágios

```text
POST /api/v1/legal/answer (USER QUERY + REFERENCE DATE)
      ↓
1. QUERY NORMALIZATION (LegalQueryNormalizer)
      ↓
2. HYBRID RETRIEVAL (Full-Text Search + Semantic Vector Similarity)
      ↓
3. TEMPORAL FILTER (TemporalIntegrityValidator.is_date_in_range(reference_date))
      ↓
4. PROVENANCE VALIDATION (Check 5-link chain)
      ↓
5. CONFLICT DETECTION (ConflictGuard for version/temporal gaps)
      ↓
6. CONTEXT ASSEMBLY (LegalContextBuilder -> LegalContextPack)
      ↓
7. LLM GENERATION (LegalAnswerGenerator / Prompt Injection Defense)
      ↓
8. ANSWER VALIDATION (LegalAnswerGuard)
      ↓
9. CITATION VALIDATION (CitationValidator -> 0 fake citations)
      ↓
10. TEMPORAL & PROVENANCE RE-CHECK (TemporalAnswerGuard & ProvenanceGuard)
      ↓
11. FINAL LEGAL RESPONSE (LegalAnswer DTO)
```

---

# 2. Princípio da Separação entre Fato Jurídico e Síntese Linguística

- **Verdade Jurídica (Legal Truth):** 100% contida nos dados relacionais canônicos.
- **Modelo de Linguagem (LLM):** Atua exclusivamente como componente de redação linguística sob um contexto estritamente fechado.
- **Abstenção Automática:** Se não houver evidências no banco ou houver conflito de versões, o sistema retorna abstenção estruturada (`INSUFFICIENT_EVIDENCE` ou `CONFLICTING_SOURCES`).
