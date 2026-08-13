# LÉXORA — Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.9.1-contextual-rag-production-lock] - 2026-08-13

### Corrigido & Selado
- **Phase 6.2 Production Correction Lock (Prompt 10):**
  - Instanciação de gerador no endpoint HTTP `/api/v1/legal/answer` atualizada para utilizar `LegalAnswerGeneratorFactory.get_generator()`, eliminando instâncias diretas de Mocks em produção (lança `ConfigurationError` se unconfigurado).
  - Estruturação de respostas com a entidade `AnswerClaim` (`claim_id`, `text`, `citation_ids`) exigindo citações válidas pertencentes ao `LegalContextPack` em cada afirmação.
  - Validação cruzada rigorosa dos 12 campos no `CitationValidator` (`legal_node_id`, `legal_version_id`, `legal_document_id`, `node_type`, `identifier`, `label`, `excerpt`, `effective_from`, `effective_until`, `source_id`, `evidence_id`, `raw_artifact_hash`).
  - Identificadores de `pack_id` em `LegalContextBuilder` e `answer_id` tornados 100% determinísticos via SHA-256 (0 UUIDs aleatórios).
  - Suíte de 30 testes unitários de selamento em `tests/unit/test_phase6_2_production_lock.py`.
  - Relatório final de selamento em `docs/PHASE6_2_PRODUCTION_LOCK.md` (STATUS: FASE 6.2 = SEALED / FASE 6.3 = AUTHORIZED).

---

## [0.9.0-contextual-legal-rag] - 2026-08-13

### Adicionado
- **Phase 6.2 — Contextual Legal RAG & Guardrails de Resposta (Prompt 09):**
  - Implementação da porta `LegalAnswerGenerator` e adaptador `MockLegalAnswerGenerator`.
