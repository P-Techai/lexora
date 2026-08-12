# LÉXORA — Relatório de Auditoria de Prontidão para a Verdade Jurídica (Legal Truth Readiness Audit)

**Data da Auditoria:** 2026-08-12  
**Versão Auditada:** `v0.6.1-readiness-audit`  
**Resultado do Gate:** **`READY`** (0 Blockers Ativos)

---

# 1. Tabela de Avaliação das 16 Dimensões de Auditoria

| Item | Dimensão de Auditoria | Classificação | Diagnóstico e Resolução Arquitetural |
| :--- | :--- | :--- | :--- |
| **1** | **Imutabilidade Histórica** | `PASS` | *Corrigido no Gate (ADR-0011).* Revogações não alteram o status estático da versão para `REVOKED`, permitindo reprodução histórica 100% perfeita para datas $T < revocation\_date$. |
| **2** | **Modelo de Revogação Total** | `PASS` | Revogação é tratada como evento temporal (`effective_until = revocation_date`) com criação de relação `REVOKES` e evidência obrigatória. Zero `DELETE` SQL. |
| **3** | **Modelo de Revogação Parcial** | `PASS` | Afeta estritamente o nó individual (`LegalNode`), mantendo os nós irmãos (Artigos/Parágrafos) vigentes e ativos. |
| **4** | **Proveniência Jurídica (Chain)** | `PASS` | Cadeia auditável completa: `SOURCE` $\to$ `RAW ARTIFACT` $\to$ `EVIDENCE` $\to$ `LEGAL RELATION` $\to$ `LEGAL VERSION / NODE`. |
| **5** | **Hierarquia Estrutural vs. Normativa** | `PASS` | Estrutura textual é mantida por `parent_id` e `path`, enquanto relações normativas entre leis são mantidas por `LegalRelation`. |
| **6** | **Segurança de Migrations & Cascades** | `PASS` | Todas as chaves estrangeiras usam `ondelete='RESTRICT'`. Não existem cascades destrutivos em tabelas históricas. |
| **7** | **Pureza do Domínio (`src/domain/`)** | `PASS` | Auditoria confirma zero importações de SQLAlchemy, ORM ou drivers de banco em `src/domain/`. |
| **8** | **Portabilidade de Provedores** | `PASS` | Camadas de Domínio e Aplicação dependem exclusivamente de interfaces abstratas (`ports`). |
| **9** | **Resolução Temporal Determinística** | `PASS` | `TemporalLegalSearchService` é 100% determinístico e adota o intervalo semi-aberto $[effective\_from, effective\_until)$. |
| **10** | **Proibição de `datetime.now()` Implícito** | `PASS` | Todas as consultas temporais exigem a passagem explícita de `target_date`. |
| **11** | **Não-Resolução Silenciosa por IA** | `PASS` | Sobreposições temporais disparam `TEMPORAL_CONFLICT` e `CONFLITANTE`, sem resolução arbitrária por LLM. |
| **12** | **Proteção de Segurança & SSRF** | `PASS` | `URLSecurityValidator` bloqueia ativamente `localhost`, `127.0.0.1`, redes privadas (`10.x`, `172.16.x`, `192.168.x`) e metadata endpoints. |
| **13** | **Preservação de Conteúdo Bruto (Raw)** | `PASS` | `RawArtifact` armazena os bytes brutos intactos no `StorageProvider` com hash SHA-256 independente. |
| **14** | **Contratos de Parser** | `PASS` | Interface `LegalStructureParser` desacoplada para suportar os parsers reais de Leis/Constituição na Fase 5. |
| **15** | **Identidade e Confiabilidade de Fontes** | `PASS` | Separação formal entre `authority_level` (1-5) e `trust_score` (0.0-1.0) conforme ADR-0008. |
| **16** | **Reprodutibilidade em Cenários Golden** | `PASS` | Testado em `test_golden_historical_scenario.py` com múltiplos pontos temporais pré e pós-revogação. |

---

# 2. Resolução do Blocker Crítico no Gate de Auditoria

- **Diagnóstico Inicial:** Na Fase 4, a revogação de um documento alterava o atributo `version.status` para `REVOKED` estaticamente no banco. Com isso, uma consulta histórica para o ano de 2021 em um documento revogado em 2024 retornava indevidamente `REVOKED`.
- **Resolução (ADR-0011):** O campo `version.status` permanece `ACTIVE` no banco. A revogação encerra a vigência (`effective_until = revocation_date`) e grava a relação `REVOKES`. O `TemporalLegalSearchService` avalia a revogação **dinamicamente na data de referência $T$**:
  - Para $T < revocation\_date$: Retorna `EFFECTIVE` (preservando o histórico prévio).
  - Para $T \ge revocation\_date$: Retorna `REVOKED` acompanhado da evidência oficial.

---

# 3. Conclusão Final do Gate

A arquitetura do **LÉXORA** atende a 100% dos requisitos de imutabilidade, provenincia, segurança e determinismo temporal, estando declarada **`READY`** para iniciar a **FASE 5 (Ingestão Oficial de Legislação Brasileira Real)**.
