# LÉXORA — Estado Atual do Projeto

**Data da Última Atualização:** 2026-08-13  
**Fase Atual:** FASE 5 — CLOSED (Fundação Encerrada e Selada)  
**Versão Atual:** `v0.7.3-foundation-closed`  
**Status da Fundação:** **`FOUNDATION = CLOSED`**  
**Status da Fase 6:** **`FASE 6 = AUTHORIZED`**  
**Status do Projeto:** PROMPT 07.3 — PASS. Reparação Final e Selamento de Contratos de Produção Concluídos: 1) Porta `DocumentAcquisitionProvider` com contrato único `acquire(request) -> AcquisitionResult`; 2) Leitura streaming por chunks de 64KB com SHA-256 incremental e limite por `max_bytes`; 3) Proteção SSRF com resolução DNS real (A/AAAA) contra subredes privadas, loopback e metadata endpoints; 4) `SafeRedirectHandler` com max 5 redirects, `redirect_chain` capturada e bloqueio de HTTPS->HTTP downgrade; 5) Identidade lógica determinística de nós normativos (`logical_id`) independente de UUIDs; 6) Eliminação completa de `ChangeStatus.UPDATED` (substituído por `ChangeStatus.CHANGED`); 7) Relatório final em `docs/FINAL_FOUNDATION_LOCK_REPORT.md`.

---

# 1. Resumo do Progresso Recente

- **Fechamento Definitivo da Fundação (v0.7.3-foundation-closed):**
  - Assinatura unificada da porta de aquisição em `DocumentAcquisitionProvider.acquire(request: AcquisitionRequest) -> AcquisitionResult`.
  - Leitura incremental em chunks de 64KB com hash SHA-256 streaming e abort por tamanho de artefato durante a leitura.
  - Resolução DNS real para A e AAAA no `URLSecurityValidator` bloqueando IPs privados e loopback.
  - Safe redirect handler com até 5 redirecionamentos e barreira contra downgrade de HTTPS para HTTP.
  - Identidade lógica canônica (`LegalNode.logical_id`) e hash canônico determinístico.
  - Suíte de contratos globais em `tests/unit/test_final_foundation_contract.py` e reprodutibilidade em `test_reproducibility_and_reingestion.py`.
- **Documentação & Relatórios Finais:**
  - `ADR-0014-final-foundation-production-contract.md`, `docs/FINAL_FOUNDATION_LOCK.md`, `docs/FINAL_FOUNDATION_LOCK_REPORT.md` (STATUS: CLOSED / AUTHORIZED).
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
│       └── 0005_phase5_normative_acts.py
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
│   │   └── ADR-0014-final-foundation-production-contract.md
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
│   ├── LEGAL_INTEGRITY.md
│   ├── LEGAL_INTEGRITY_HARDENING.md
│   ├── LEGAL_INTEGRITY_HARDENING_REPORT.md
│   ├── LEGAL_MODEL.md
│   ├── LEGAL_TRUTH_READINESS.md
│   ├── OFFICIAL_SOURCES.md
│   ├── PARSER_ARCHITECTURE.md
│   ├── PHASE5_COMPLETION_GATE.md
│   ├── PHASE5_PILOT_DATASET.md
│   ├── PHASE5_PREIMPLEMENTATION_AUDIT.md
│   ├── PROJECT.md
│   ├── PROJECT_MEMORY.md
│   ├── RAW_ARTIFACTS.md
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
│   │   │   ├── ingestion_dto.py
│   │   │   └── temporal_dto.py
│   │   ├── parsers/
│   │   │   └── brazilian_law_parser.py
│   │   ├── ports/
│   │   │   ├── acquisition_provider.py
│   │   │   ├── database_provider.py
│   │   │   ├── document_extractor.py
│   │   │   ├── llm_provider.py
│   │   │   ├── repositories.py
│   │   │   ├── retrieval_ports.py
│   │   │   ├── storage_provider.py
│   │   │   └── structure_parser.py
│   │   ├── services/
│   │   │   └── source_registry.py
│   │   └── use_cases/
│   │       └── legal/
│   │           ├── add_legal_nodes.py
│   │           ├── acquire_artifact.py
│   │           ├── create_document.py
│   │           ├── create_legal_relation.py
│   │           ├── create_version.py
│   │           ├── ingest_document.py
│   │           ├── query_legal_at_date.py
│   │           ├── revoke_legal_document.py
│   │           ├── revoke_legal_node.py
│   │           └── validate_temporal_integrity.py
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── acquisition_audit_log.py
│   │   │   ├── evidence.py
│   │   │   ├── legal_document.py
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
│   │   │   ├── temporal_search_service.py
│   │   │   ├── temporal_validator.py
│   │   │   ├── tree_validator.py
│   │   │   └── url_validator.py
│   │   ├── enums.py
│   │   └── exceptions.py
│   ├── infrastructure/
│   │   ├── adapters/
│   │   │   ├── html_txt_extractor.py
│   │   │   ├── http_acquisition.py
│   │   │   ├── local_storage.py
│   │   │   ├── mock_acquisition.py
│   │   │   └── mock_llm.py
│   │   └── db/
│   │       ├── models/
│   │       │   ├── acquisition_audit_model.py
│   │       │   ├── evidence_model.py
│   │       │   ├── legal_document_model.py
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
│   │   ├── test_golden_pilot_documents.py
│   │   ├── test_postgres_connection.py
│   │   ├── test_postgres_evidence_referential_protection.py
│   │   ├── test_postgres_real.py
│   │   ├── test_postgres_schema_audit.py
│   │   ├── test_temporal_use_cases.py
│   │   └── test_use_cases.py
│   └── unit/
│       ├── test_acquisition_security.py
│       ├── test_brazilian_law_parser.py
│       ├── test_domain.py
│       ├── test_domain_canonical.py
│       ├── test_final_foundation_contract.py
│       ├── test_forensic_foundation_audit.py
│       ├── test_ingestion_pipeline.py
│       ├── test_ports.py
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

**FASE 6 — Legal RAG & Vector Indexing (AUTORIZADA)**
1. Implementar portas de indexação vetorial e reranking por hierarquia jurídica conforme ADR-0005;
2. Integrar busca híbrida (Busca Vetorial + Busca Lexical Canônica) vinculada estritamente a referências normativas vigentes;
3. Manter a barreira determinística do Legal Brain intacta (a LLM nunca altera o fato jurídico).
