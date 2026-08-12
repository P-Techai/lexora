# LÉXORA — Estado Atual do Projeto

**Data da Última Atualização:** 2026-08-12  
**Fase Atual:** PROMPT 06.3 — PostgreSQL Reality & State Consistency Gate  
**Versão Atual:** `v0.6.4-integrity-verification`  
**Status do Projeto:** FASE 06.3 — PASS. Validação empírica concluída: 1) Suporte a testes duais SQLite (auxiliar) e PostgreSQL autoritativo em `tests/integration/test_evidence_referential_protection.py`; 2) Auditoria direta de catálogo no HEAD (`0004`) confirmando `CASCADE = 0` e `SET NULL = 0` em `tests/integration/test_postgres_schema_audit.py`; 3) Cadeia de migrations `0001` a `0004` e round-trip testados; 4) Correção de todos os caminhos absolutos para caminhos relativos portáveis em `docs/HANDOFF.md` e documentação operacional.

---

# 1. Resumo do Progresso Recente

- **Suporte a Banco Dual (PostgreSQL Autoritativo & SQLite Auxiliar):**
  - Atualizado `test_evidence_referential_protection.py` para suportar execução dual via `TEST_DATABASE_URL`. Rejeição de exclusões (`RESTRICT`) para `LegalDocument`, `LegalVersion` e `LegalNode` vinculados a `Evidence` fisicamente validada em motor relacional.
- **Auditoria Direta de Schema no HEAD (0004):**
  - Criado `test_postgres_schema_audit.py` inspecionando o catálogo de constraints. Confirmado que no `HEAD` (`0004`) o número de FKs jurídicas com `CASCADE` é 0 e com `SET NULL` é 0.
- **Hardening de Portabilidade na Documentação:**
  - Removidos todos os caminhos absolutos de desenvolvimento (`file:///c:/Users/Pedro/...`) de `docs/HANDOFF.md` e arquivos operacionais, substituindo por links relativos do repositório (`docs/PROJECT.md`, `docs/HANDOFF.md`).
- **Documentação & Relatório Final:**
  - `docs/LEGAL_INTEGRITY_HARDENING.md`, `docs/LEGAL_INTEGRITY_HARDENING_REPORT.md` (STATUS: FASE 06.3 — PASS) e `ADR-0012`.
- **Status Cloud:** Neon = NÃO INTEGRADO, Supabase = NÃO INTEGRADO, Cloudflare = NÃO INTEGRADO.

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
│       └── 0004_evidence_fk_integrity.py
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
│   │   └── ADR-0012-legal-integrity-hardening.md
│   ├── ACQUISITION.md
│   ├── AGENT_PROTOCOL.md
│   ├── ARCHITECTURE.md
│   ├── CHANGELOG.md
│   ├── CURRENT_STATE.md
│   ├── DATABASE.md
│   ├── DECISIONS.md
│   ├── HANDOFF.md
│   ├── INGESTION.md
│   ├── LEGAL_INTEGRITY.md
│   ├── LEGAL_INTEGRITY_HARDENING.md
│   ├── LEGAL_INTEGRITY_HARDENING_REPORT.md
│   ├── LEGAL_MODEL.md
│   ├── LEGAL_TRUTH_READINESS.md
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
│   │   ├── ports/
│   │   │   ├── acquisition_provider.py
│   │   │   ├── database_provider.py
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
│   │   ├── test_database.py
│   │   ├── test_evidence_referential_protection.py
│   │   ├── test_golden_historical_scenario.py
│   │   ├── test_postgres_real.py
│   │   ├── test_postgres_schema_audit.py
│   │   ├── test_temporal_use_cases.py
│   │   └── test_use_cases.py
│   └── unit/
│       ├── test_acquisition_security.py
│       ├── test_domain.py
│       ├── test_domain_canonical.py
│       ├── test_ingestion_pipeline.py
│       ├── test_ports.py
│       ├── test_revocation_behavior.py
│       ├── test_security_governance_audit.py
│       ├── test_source_governance.py
│       ├── test_temporal_integrity.py
│       └── test_temporal_semantics.py
├── .env.example
├── .gitignore
├── alembic.ini
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

# 3. Próxima Tarefa Prioritária

**FASE 5 — Ingestão Oficial & Parsers de Legislação Real**
1. Implementar os conectores de leitura para os portais oficiais primários (Planalto, Receita Federal, CONFAZ);
2. Desenvolver os parsers estruturais especializados para a Constituição Federal, Leis Complementares e Ordinárias;
3. Realizar a primeira ingestão oficial controlada na base canônica do LÉXORA.
