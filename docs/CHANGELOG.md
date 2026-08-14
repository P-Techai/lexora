# LÉXORA — Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.10.0-fiscal-brain-foundation] - 2026-08-14

### Adicionado
- **Phase 6.3 — Fiscal Brain & Decision Engine — Two-Brain Governance (Prompt 11):**
  - Implementação da arquitetura Two-Brain desacoplada (Legal Brain + Fiscal Brain + Decision Engine).
  - Entidades de domínio fiscal e decisão (`FiscalFact`, `FiscalProductProfile`, `FiscalTaxRule`, `TaxCalculation`, `TaxCalculationLog`, `Decision`, `DecisionTrace`, `CompanyFiscalProfile`).
  - Motor de cálculo tributário Decimal estrito (`TaxRoundingService` `ROUND_HALF_UP`) cobrindo ICMS, ICMS_ST, IPI, PIS, COFINS, ISS, CBS, IBS, IS sem o uso de float ou I.A./LLM.
  - Avaliação de vigência temporal baseada em `operation_date` via `TemporalIntegrityValidator.is_date_in_range()`.
  - Parser seguro de NFe XML (`SecureNFeParser`) com proteção contra XXE, Billion Laughs, limites de tamanho e verificação de idempotência SHA-256 (`raw_xml_hash`).
  - Migration Alembic `0008_fiscal_brain` criando tabelas com FKs protegidas por `ON DELETE RESTRICT`.
  - Endpoints REST `/api/v1/fiscal/classify`, `/api/v1/fiscal/calculate`, `/api/v1/fiscal/decide`, `/api/v1/nfe/import`.
  - Suíte de 40 cenários de testes unitários em `tests/unit/test_fiscal_brain.py` e testes de integração PostgreSQL em `tests/integration/test_postgres_fiscal.py`.
  - Documentação em `docs/FISCAL_BRAIN.md`, `docs/DECISION_ENGINE.md`, `docs/TWO_BRAINS_ARCHITECTURE.md`, `docs/NFE_PARSING.md` e `ADR-0017-fiscal-brain-decision-engine.md`.

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
