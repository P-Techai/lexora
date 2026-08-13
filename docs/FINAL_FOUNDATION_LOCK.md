# LÉXORA — Selamento Definitivo da Fundação (Final Foundation Lock Specification)

**Versão da Fundação:** `v0.7.3-foundation-closed`  
**Data de Selamento:** 2026-08-13  
**Status da Fundação:** **`FOUNDATION = CLOSED`**  
**Status da Fase 6:** **`FASE 6 = AUTHORIZED`**

---

# 1. Princípios de Selamento de Produção

A fundação do **LÉXORA (LXR)** está formalmente encerrada e selada. Todas as 5 fases fundacionais (Constituição, Modelo Canônico, Ingestion Contracts, Source Governance, Temporal Truth, Ingestão Oficial de Legislação Brasileira Real) foram auditadas, corrigidas e comprovadas empiricamente.

---

# 2. Resumo de Especificações Canônicas Seladas

1. **Clean Architecture de 4 Camadas Puras:** `src/domain/` possui ZERO importações externas (0 ORM, 0 HTTP, 0 SDKs).
2. **Contrato de Aquisição Unificado:** `DocumentAcquisitionProvider.acquire(request: AcquisitionRequest) -> AcquisitionResult`.
3. **Download Streaming em Chunks (64KB):** SHA-256 incremental e verificação estrita de `max_bytes` durante o streaming.
4. **Proteção SSRF com Resolução DNS Real:** Resolução A e AAAA para todos os hostnames e bloqueio estrito de faixas de IP privadas, loopback e metadados.
5. **Safe Redirect Handler:** Limite de 5 redirects com captura de `redirect_chain` e bloqueio de downgrade HTTPS $\to$ HTTP.
6. **Identidade Lógica Determinística:** `LegalNode.logical_id` derivada de `f"{legal_version_id}:{path}"` e hash canônico determinístico.
7. **Eliminação de Símbolos Legados:** 0 ocorrências de `ChangeStatus.UPDATED` (substituído por `ChangeStatus.CHANGED`).
8. **Matemática Temporal Única:** `TemporalIntegrityValidator.is_date_in_range` centralizando intervalos semi-abertos $[effective\_from, effective\_until)$.
9. **Catálogo Relacional PostgreSQL:** Schema e migrations Alembic (`0001` a `0005`) com 0 `CASCADE` e 0 `SET NULL` em tabelas normativas e de evidência (`RESTRICT`).

---

# 3. Autorização Explícita da FASE 6

A **FASE 6 — Legal RAG & Vector Indexing** está **OFICIALMENTE AUTORIZADA**.
O desenvolvimento do próximo prompt poderá prosseguir diretamente para a implementação das capacidades de produção da plataforma.
