# LÉXORA — Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.6.0-temporal-truth] - 2026-08-12

### Adicionado
- **Advanced Legal Versioning & Temporal Truth (Fase 4):**
  - Definição das 4 dimensões temporais (`publication_date`, `effective_from`, `effective_until`, `captured_at`).
  - Matemática de intervalo semi-aberto $[effective\_from, effective\_until)$.
  - Enums `TemporalStatus` (`EFFECTIVE`, `NOT_YET_EFFECTIVE`, `EXPIRED`, `REVOKED`, `TEMPORAL_GAP`, `TEMPORAL_CONFLICT`, `NOT_FOUND`) e `RevocationType`.
- **Serviços Temporais de Domínio:**
  - `TemporalIntegrityValidator`: Auditoria de séries de versões, detecção de sobreposição de vigência (`OVERLAP` -> `TEMPORAL_CONFLICT`) e lacunas (`GAP` -> `TEMPORAL_GAP`).
  - `TemporalLegalSearchService`: Resolução determinística da Verdade Jurídica em uma data de referência $T$ e filtro de consistência de versão da árvore normativa.
- **Modelo Imutável de Revogação Total e Parcial:**
  - `RevokeLegalDocumentUseCase`: Revogação total por encerramento de vigência e associação obrigatória de `Evidence` (0 comandos `DELETE` SQL).
  - `RevokeLegalNodeUseCase`: Revogação parcial de dispositivos individuais (`LegalNode`), mantendo os nós irmãos vigentes.
- **Casos de Uso da Aplicação (`src/application/use_cases/legal/`):**
  - `QueryLegalAtDateUseCase`, `RevokeLegalDocumentUseCase`, `RevokeLegalNodeUseCase`, `ValidateTemporalIntegrityUseCase`.
- **DTOs Temporais (`src/application/dto/temporal_dto.py`):** DTOs imutáveis `TemporalQueryRequest` e `TemporalLegalResult`.
- **Documentação & ADR:**
  - `docs/TEMPORAL_LEGAL_MODEL.md` (Especificação completa do modelo jurídico temporal).
  - `docs/adr/ADR-0010-temporal-legal-semantics.md` (Semântica semi-aberta e revogação imutável).
  - `.agents/rules/01_legal_truth.md` atualizada para consolidar o tempo como dimensão primária da Verdade Jurídica.
- **Suite de Testes Ampliada:**
  - `tests/unit/test_temporal_semantics.py`: Testes de limites de intervalos semi-abertos, vacatio legis e séries de versões consecutivas (A -> B -> C).
  - `tests/unit/test_temporal_integrity.py`: Testes de detecção de sobreposição de vigência (`TEMPORAL_CONFLICT`) e lacunas (`TEMPORAL_GAP`).
  - `tests/integration/test_temporal_use_cases.py`: Testes de integração para consulta temporal, revogação total e parcial com evidência, imutabilidade histórica e consistência de árvore.

---

## [0.5.0-acquisition-engine] - 2026-08-11

### Adicionado
- **Source Governance & Source Registry (Fase 3):** `SourceRegistryService`, `URLSecurityValidator` (proteção SSRF), `RawArtifact`, `AcquisitionAuditLog`, `AcquireArtifactUseCase`.
