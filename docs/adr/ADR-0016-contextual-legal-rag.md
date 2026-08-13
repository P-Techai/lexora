# ADR-0016: Arquitetura de RAG Jurídico Contextual e Guardrails de Resposta

## Context
Na Fase 6.2 do LÉXORA, implementou-se a camada de geração de respostas linguísticas (Contextual Legal RAG) e a suíte rigorosa de guardrails determinísticos de resposta. O princípio fundamental exige que modelos de linguagem (LLMs) NUNCA atuem como fonte da Verdade Jurídica, servindo exclusivamente como geradores de síntese textual a partir de um pacote de contexto fechado (`LegalContextPack`).

## Decision
1. **Regra de Ouro (`LLM ≠ SOURCE OF TRUTH`):** A verdade jurídica provém 100% de dispositivos normativos recuperados via busca híbrida, versionados e com proveniência de 5 níveis intacta.
2. **Pipeline em 11 Estágios:** Query Normalization $\to$ Hybrid Retrieval $\to$ Temporal Filter $\to$ Provenance Validation $\to$ Conflict Detection $\to$ Context Assembly $\to$ Generation $\to$ Answer Validation $\to$ Citation Validation $\to$ Final Legal Response.
3. **Orçamento de Contexto Fechado:** `LegalContextBuilder` limita rigorosamente nós normativos, contagem de caracteres e deduplica dispositivos antes de enviar ao gerador.
4. **Proteção contra Prompt Injection:** O texto dos documentos jurídicos recuperados é formatado estritamente como DADOS não executáveis, impedindo que comandos maliciosos contidos em normas alterem a conduta do sistema.
5. **Guardrails de Validação de Resposta:** `LegalAnswerGuard` orquestra validadores automáticos:
   - `CitationValidator`: rejeita respostas com citações inventadas ou ausentes no contexto.
   - `TemporalAnswerGuard`: valida vigência na `reference_date` usando `TemporalIntegrityValidator.is_date_in_range`.
   - `ProvenanceGuard`: exige cadeia de 5 níveis (`Node -> Version -> Evidence -> RawArtifact -> Source`).
   - `ConflictGuard` e `AbstentionPolicy`: geram respostas estruturadas de abstenção quando ocorrem conflitos normativos ou insuficiência de evidência.
6. **Estados do DTO `LegalAnswer`:** Enum `LegalAnswerStatus` (`SUPPORTED`, `PARTIALLY_SUPPORTED`, `INSUFFICIENT_EVIDENCE`, `TEMPORAL_CONFLICT`, `TEMPORAL_GAP`, `PROVENANCE_FAILURE`, `CONFLICTING_SOURCES`, `ABSTAINED`).

## Consequences
- Sistema de RAG Jurídico imune a alucinações de citações e violações temporais.
- **Status da Fase 6.2:** **`COMPLETE`**
- **Status da Fase 6.3:** **`AUTHORIZED`**
