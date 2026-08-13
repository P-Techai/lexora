# LÉXORA — Estado Atual do Projeto

**Data da Última Atualização:** 2026-08-13  
**Fase Atual:** FASE 6.2 — SEALED (Selamento de Produção do RAG Jurídico Contextual)  
**Versão Atual:** `v0.9.1-contextual-rag-production-lock`  
**Status da Fase 6.2:** **`FASE 6.2 = SEALED`**  
**Status da Fase 6.3:** **`FASE 6.3 = AUTHORIZED`**  
**Status do Projeto:** PROMPT 10 — PASS. Selamento Definitivo de Produção do RAG Jurídico Contextual: 1) Instanciação do gerador no endpoint HTTP `/api/v1/legal/answer` via `LegalAnswerGeneratorFactory.get_generator()` com bloqueio estrito de fallbacks silenciosos em produção (`ConfigurationError`); 2) Entidade `AnswerClaim` com validação de citação por afirmação; 3) Validação cruzada rigorosa dos 12 campos no `CitationValidator`; 4) IDs de `LegalContextPack` (`pack_id`) e `LegalAnswer` (`answer_id`) 100% determinísticos via SHA-256 (0 UUIDs aleatórios); 5) Suíte de 30 cenários de selamento em `tests/unit/test_phase6_2_production_lock.py`; 6) Documentação alinhada em `docs/PHASE6_2_PRODUCTION_LOCK.md`.

---

# 1. Resumo do Progresso Recente

- **Selamento de Produção do RAG Jurídico Contextual (v0.9.1-contextual-rag-production-lock):**
  - Eliminação de chamadas diretas a Mocks no endpoint HTTP `/api/v1/legal/answer`.
  - Provedores carregados dinamicamente via `LegalAnswerGeneratorFactory`. Em ambiente de produção, falhas de configuração lançam `ConfigurationError` sem fallback para Mock.
  - Estruturação de respostas com `AnswerClaim` exigindo que toda afirmação jurídica contenha citações válidas pertencentes ao `LegalContextPack`.
  - Validação cruzada dos 12 campos de cada citação (`node_id`, `version_id`, `doc_id`, `node_type`, `identifier`, `label`, `excerpt`, `effective_from`, `effective_until`, `source_id`, `evidence_id`, `raw_artifact_hash`).
  - Geração determinística de `pack_id` e `answer_id` garantindo reprodutibilidade idêntica.
  - Suíte de 30 testes unitários e de integração validando a integridade da camada de RAG.
- **Documentação & Relatórios Finais:**
  - `docs/PHASE6_2_PRODUCTION_LOCK.md` (STATUS: FASE 6.2 = SEALED / FASE 6.3 = AUTHORIZED).
- **Status Cloud:** Neon = INTEGRADO VIA DATABASE_URL; Supabase = NÃO INTEGRADO; Cloudflare = NÃO INTEGRADO.

---

# 2. Árvore de Diretórios do Repositório

```
lexora/
├── .agents/
│   ├── rules/
│   │   ├── 01_legal_truth.md
│   │   ├── 02_architecture_portability.md
│   │   ├── 03_calculation_determinism.md
│   │   ├── 04_handoff_documentation.md
│   │   ├── 05_identity_personality_trust.md
│   │   ├── 06_two_brains_decision_engine.md
│   │   ├── 07_source_trust_and_versioning.md
│   │   ├── 08_autonomous_agent_safety.md
│   │   └── 10_change_control.md
│   └── workflows/
│       ├── development.md
│       ├── handoff.md
│       └── start_session.md
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 0001_canonical_legal_model.py
│       ├── 0002_acquisition_and_artifacts.py
│       ├── 0003_legal_integrity_hardening.py
│       ├── 0004_evidence_fk_integrity.py
│       ├── 0005_phase5_normative_acts.py
│       ├── 0006_phase6_retrieval.py
│       └── 0007_phase6_vector_fts.py
├── docs/
│   ├── adr/
│   │   ├── ADR-0001-clean-architecture.md
│   │   ├── ADR-0002-vendor-portability-free-tier.md
│   │   ├── ADR-0003-legal-truth-llm-guardrails.md
│   │   ├── ADR-0004-deterministic-tax-calculation.md
│   │   ├── ADR-0005-hybrid-rag-legal-hierarchy.md
│   │   ├── ADR-0006-two-brains-and-decision-engine.md
│   │   ├── ADR-0007-canonical-legal-data-model.md
│   │   ├── ADR-0008-source-authority-vs-source-trust.md
│   │   ├── ADR-0009-source-governance-and-acquisition-security.md
│   │   ├── ADR-0010-temporal-legal-semantics.md
│   │   ├── ADR-0011-dynamic-temporal-revocation-resolution.md
│   │   ├── ADR-0012-legal-integrity-hardening.md
│   │   ├── ADR-0013-brazilian-legal-parsers-and-normative-acts.md
│   │   ├── ADR-0014-final-foundation-production-contract.md
│   │   ├── ADR-0015-hybrid-legal-retrieval.md
│   │   └── ADR-0016-contextual-legal-rag.md
│   ├── ACQUISITION.md
│   ├── AGENT_PROTOCOL.md
│   ├── ARCHITECTURE.md
│   ├── CHANGELOG.md
│   ├── CURRENT_STATE.md
│   ├── DATABASE.md
│   ├── DATABASE_TRUTH_GATE.md
│   ├── DECISIONS.md
│   ├── DOCUMENT_EXTRACTION.md
│   ├── FINAL_FOUNDATION_AUDIT.md
│   ├── FINAL_FOUNDATION_CONSISTENCY_REPORT.md
│   ├── FINAL_FOUNDATION_LOCK.md
│   ├── FINAL_FOUNDATION_LOCK_REPORT.md
│   ├── HANDOFF.md
│   ├── INGESTION.md
│   ├── LEGAL_ANSWER_GUARDRAILS.md
│   ├── LEGAL_INTEGRITY.md
│   ├── LEGAL_INTEGRITY_HARDENING.md
│   ├── LEGAL_INTEGRITY_HARDENING_REPORT.md
│   ├── LEGAL_MODEL.md
│   ├── LEGAL_RAG_ARCHITECTURE.md
│   ├── LEGAL_TRUTH_READINESS.md
│   ├── OFFICIAL_SOURCES.md
│   ├── PARSER_ARCHITECTURE.md
│   ├── PHASE5_COMPLETION_GATE.md
│   ├── PHASE5_PILOT_DATASET.md
│   ├── PHASE5_PREIMPLEMENTATION_AUDIT.md
│   ├── PHASE6_1_COMPLETION.md
│   ├── PHASE6_1_RETRIEVAL_PRODUCTION_CLOSURE.md
│   ├── PHASE6_2_COMPLETION.md
│   ├── PHASE6_2_PRODUCTION_LOCK.md
│   ├── PROJECT.md
│   ├── PROJECT_MEMORY.md
│   ├── RAW_ARTIFACTS.md
│   ├── RETRIEVAL_ARCHITECTURE.md
│   ├── ROADMAP.md
│   ├── SOURCE_GOVERNANCE.md
│   └── TEMPORAL_LEGAL_MODEL.md
├── infrastructure/
│   ├── docker-compose.yml
│   └── README.md
├── specs/
│   ├── fiscal_engine_spec.md
│   ├── legal_domain_spec.md
│   ├── nfe_parsing_spec.md
│   └── reforma_tributaria_spec.md
├── src/
│   ├── application/
│   │   ├── dto/
│   │   │   ├── acquisition_dto.py
│   │   │   ├── context_pack.py
│   │   │   ├── ingestion_dto.py
│   │   │   ├── retrieval_dto.py
│   │   │   └── temporal_dto.py
│   │   ├── parsers/
│   │   │   └── brazilian_law_parser.py
│   │   ├── ports/
│   │   │   ├── acquisition_provider.py
│   │   │   ├── database_provider.py
│   │   │   ├── document_extractor.py
│   │   │   ├── embedding_provider.py
│   │   │   ├── legal_answer_generator.py
│   │   │   ├── llm_provider.py
│   │   │   ├── repositories.py
│   │   │   ├── retrieval_ports.py
│   │   │   ├── storage_provider.py
│   │   │   └── structure_parser.py
│   │   ├── services/
│   │   │   ├── context_builder.py
│   │   │   ├── embedding_indexer.py
│   │   │   ├── source_registry.py
│   │   │   └── guardrails/
│   │   │       ├── abstention_policy.py
│   │   │       ├── answer_guard.py
│   │   │       ├── citation_validator.py
│   │   │       ├── conflict_guard.py
│   │   │       ├── provenance_guard.py
│   │   │       └── temporal_guard.py
│   │   └── use_cases/
│   │       ├── legal/
│   │       │   ├── add_legal_nodes.py
│   │       │   ├── acquire_artifact.py
│   │       │   ├── create_document.py
│   │       │   ├── create_legal_relation.py
│   │       │   ├── create_version.py
│   │       │   ├── ingest_document.py
│   │       │   ├── query_legal_at_date.py
│   │       │   ├── revoke_legal_document.py
│   │       │   ├── revoke_legal_node.py
│   │       │   └── validate_temporal_integrity.py
│   │       └── retrieval/
│   │           ├── retrieve_and_answer.py
│   │           ├── retrieve_legal_evidence.py
│   │           └── retrieve_legal_information.py
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── acquisition_audit_log.py
│   │   │   ├── evidence.py
│   │   │   ├── legal_answer.py
│   │   │   ├── legal_document.py
│   │   │   ├── legal_embedding.py
│   │   │   ├── legal_node.py
│   │   │   ├── legal_relation.py
│   │   │   ├── legal_version.py
│   │   │   ├── raw_artifact.py
│   │   │   ├── source.py
│   │   │   └── tax_calculation.py
│   │   ├── services/
│   │   │   ├── change_detection.py
│   │   │   ├── hash_service.py
│   │   │   ├── identity_matcher.py
│   │   │   ├── normalization_service.py
│   │   │   ├── path_builder.py
│   │   │   ├── query_normalizer.py
│   │   │   ├── retrieval_text_builder.py
│   │   │   ├── temporal_search_service.py
│   │   │   ├── temporal_validator.py
│   │   │   ├── tree_validator.py
│   │   │   └── url_validator.py
│   │   ├── enums.py
│   │   └── exceptions.py
│   ├── infrastructure/
│   │   ├── adapters/
│   │   │   ├── factory.py
│   │   │   ├── html_txt_extractor.py
│   │   │   ├── http_acquisition.py
│   │   │   ├── local_storage.py
│   │   │   ├── mock_acquisition.py
│   │   │   ├── mock_embedding.py
│   │   │   ├── mock_legal_answer_generator.py
│   │   │   └── mock_llm.py
│   │   └── db/
│   │       ├── models/
│   │       │   ├── acquisition_audit_model.py
│   │       │   ├── evidence_model.py
│   │       │   ├── legal_document_model.py
│   │       │   ├── legal_embedding_model.py
│   │       │   ├── legal_node_model.py
│   │       │   ├── legal_relation_model.py
│   │       │   ├── legal_version_model.py
│   │       │   ├── raw_artifact_model.py
│   │       │   └── source_model.py
│   │       ├── repositories/
│   │       │   └── postgres_repositories.py
│   │       ├── base.py
│   │       └── session.py
│   └── interfaces/
│       └── api/
│           └── main.py
├── tests/
│   ├── integration/
│   │   ├── test_acquisition_pipeline.py
│   │   ├── test_alembic.py
│   │   ├── test_concurrency_race_conditions.py
│   │   ├── test_database.py
│   │   ├── test_end_to_end_acquisition_ingestion.py
│   │   ├── test_evidence_referential_protection.py
│   │   ├── test_golden_historical_scenario.py
│   │   ├── test_golden_legal_rag_e2e.py
│   │   ├── test_golden_pilot_documents.py
│   │   ├── test_golden_temporal_provenance_retrieval.py
│   │   ├── test_phase6_retrieval_end_to_end.py
│   │   ├── test_postgres_connection.py
│   │   ├── test_postgres_evidence_referential_protection.py
│   │   ├── test_postgres_real.py
│   │   ├── test_postgres_schema_audit.py
│   │   ├── test_temporal_use_cases.py
│   │   └── test_use_cases.py
│   └── unit/
│       ├── test_acquisition_security.py
│       ├── test_brazilian_law_parser.py
│       ├── test_canonical_retrieval_text.py
│       ├── test_deterministic_hybrid_ranking.py
│       ├── test_domain.py
│       ├── test_domain_canonical.py
│       ├── test_final_foundation_contract.py
│       ├── test_forensic_foundation_audit.py
│       ├── test_ingestion_pipeline.py
│       ├── test_legal_rag_guardrails.py
│       ├── test_no_production_stubs.py
│       ├── test_phase6_2_production_lock.py
│       ├── test_ports.py
│       ├── test_query_normalizer.py
│       ├── test_reproducibility_and_reingestion.py
│       ├── test_revocation_behavior.py
│       ├── test_security_governance_audit.py
│       ├── test_source_governance.py
│       ├── test_temporal_integrity.py
│       └── test_temporal_semantics.py
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

# 3. Próxima Tarefa Prioritária

**FASE 6.3 — FISCAL BRAIN & DECISION ENGINE (AUTORIZADA)**
1. Implementar a separação conceitual do Fiscal Brain para classificação e regras tributárias (ICMS, PIS/COFINS, ISS, IBS/CBS/IS);
2. Construir o Decision Engine auditável determinístico com rastreabilidade total até a base legal selada da Fase 6.2;
3. Integrar os 2 Cérebros (Legal Brain + Fiscal Brain) sob a governança temporal.
