# LÉXORA — Estado Atual do Projeto

**Data da Última Atualização:** 2026-08-12  
**Fase Atual:** FASE 4 — Advanced Legal Versioning & Temporal Truth  
**Versão Atual:** `0.6.0-temporal-truth`  
**Status do Projeto:** Fase 4 concluída com sucesso. Matemática temporal de intervalos semi-abertos `[effective_from, effective_until)`, validador de sobreposição de vigências (`TEMPORAL_CONFLICT`) e lacunas (`TEMPORAL_GAP`), serviço de busca temporal determinístico (`TemporalLegalSearchService`), modelo imutável de revogação total e parcial sem comandos `DELETE` SQL, casos de uso temporais, auditoria de consistência de versão da árvore normativa, regra de agente 01 atualizada e ADR-0010 concluídos.

---

# 1. Resumo do Progresso Recente

- **Semântica Temporal de Intervalos Semi-Abertos $[effective\_from, effective\_until)$:**
  - Implementada resolução exata de vigência em qualquer data de referência $T$.
  - Enum `TemporalStatus` (`EFFECTIVE`, `NOT_YET_EFFECTIVE`, `EXPIRED`, `REVOKED`, `TEMPORAL_GAP`, `TEMPORAL_CONFLICT`, `NOT_FOUND`).
- **Validação de Integridade Temporal (`TemporalIntegrityValidator`):**
  - Detecção rigorosa de sobreposições de vigência (`OVERLAP` -> `TEMPORAL_CONFLICT`) sem resolução silenciosa por IA.
  - Detecção de lacunas temporais sem cobertura normativa (`GAP` -> `TEMPORAL_GAP`).
- **Serviço de Busca Temporal (`TemporalLegalSearchService`):**
  - Resolução de vigência por documento e data de referência $T$.
  - Validação da consistência de versão da árvore normativa (impede a mistura de nós de versões diferentes).
- **Modelo Imutável de Revogação Total e Parcial:**
  - `RevokeLegalDocumentUseCase` (Revogação total atualiza vigência e status sem excluir dados do banco).
  - `RevokeLegalNodeUseCase` (Revogação parcial afeta apenas o nó alvo, mantendo os nós irmãos vigentes).
  - Exigência estrita de proveniência de evidência (`Evidence`) para revogações.
- **Casos de Uso da Aplicação (`src/application/use_cases/legal/`):**
  - `QueryLegalAtDateUseCase`, `RevokeLegalDocumentUseCase`, `RevokeLegalNodeUseCase`, `ValidateTemporalIntegrityUseCase`.
- **Governança & Regra de Agente:**
  - `.agents/rules/01_legal_truth.md` atualizada para consagrar o tempo como dimensão primária da Verdade Jurídica.
- **Documentação Adicionada:**
  - `docs/TEMPORAL_LEGAL_MODEL.md` e `ADR-0010`.

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
│       └── 0002_acquisition_and_artifacts.py
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
│   │   └── ADR-0010-temporal-legal-semantics.md
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
│   ├── LEGAL_MODEL.md
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
│   │   ├── test_postgres_real.py
│   │   ├── test_temporal_use_cases.py
│   │   └── test_use_cases.py
│   └── unit/
│       ├── test_acquisition_security.py
│       ├── test_domain.py
│       ├── test_domain_canonical.py
│       ├── test_ingestion_pipeline.py
│       ├── test_ports.py
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
1. Implementar o conector de leitura sintética/mock para atuar sobre a estrutura da Constituição Federal e Leis Complementares;
2. Desenvolver os parsers normativos capazes de extrair a hierarquia real de artigos, parágrafos, incisos e alíneas;
3. Integrar a ingestão oficial com o pipeline determinístico e temporal construído nas Fases 1-4.
