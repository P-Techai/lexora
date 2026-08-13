# LÉXORA — Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.9.0-contextual-legal-rag] - 2026-08-13

### Adicionado
- **Phase 6.2 — Contextual Legal RAG & Guardrails de Resposta (Prompt 09):**
  - Implementação da porta `LegalAnswerGenerator` em `src/application/ports/legal_answer_generator.py` e adaptador `MockLegalAnswerGenerator`.
  - Enum `LegalAnswerStatus` (`SUPPORTED`, `PARTIALLY_SUPPORTED`, `INSUFFICIENT_EVIDENCE`, `TEMPORAL_CONFLICT`, `TEMPORAL_GAP`, `PROVENANCE_FAILURE`, `CONFLICTING_SOURCES`, `ABSTAINED`) e DTO `LegalAnswer`.
  - Construtor determinístico de pacote de contexto `LegalContextBuilder` com controle de orçamento (max nodes, max chars, deduplicação).
  - Suíte de Guardrails em `src/application/services/guardrails/`:
    - `CitationValidator` (rejeição de citações inventadas ou não fundamentadas).
    - `TemporalAnswerGuard` (validação de vigência na `reference_date`).
    - `ProvenanceGuard` (validação de proveniência de 5 níveis).
    - `ConflictGuard` (detecção de conflitos de versões e lacunas).
    - `AbstentionPolicy` (abstenção estruturada determinística).
    - `LegalAnswerGuard` (orquestrador de validação).
  - Proteção contra ataques de Prompt Injection em documentos normativos (tratados estritamente como DADOS não executáveis em aspas).
  - Endpoint da API `POST /api/v1/legal/answer` publicado na FastAPI.
  - Caso de uso `RetrieveAndAnswerUseCase` conectando recuperação de 7 estágios e geração/validação de 4 estágios (11 estágios no total).
  - Suíte de testes unitários `test_legal_rag_guardrails.py` e teste de integração Golden E2E `test_golden_legal_rag_e2e.py`.
  - Especificações `docs/LEGAL_RAG_ARCHITECTURE.md`, `docs/LEGAL_ANSWER_GUARDRAILS.md`, relatório `docs/PHASE6_2_COMPLETION.md` e ADR-0016.

---

## [0.8.1-retrieval-production-closure] - 2026-08-13

### Adicionado
- **Retrieval Implementation Closure & Production-Grade RAG Foundation (Prompt 08.1):**
  - Endpoint HTTP `/api/v1/legal/retrieve` refatorado para executar a classe de uso real `RetrieveLegalInformationUseCase`.
