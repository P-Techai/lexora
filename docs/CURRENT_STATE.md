# LÉXORA — ESTADO ATUAL DA PLATAFORMA (CURRENT STATE)

**Versão da Plataforma:** `v1.0.0-operational-fiscal-engine`  
**Data:** 2026-08-14  
**Status da Fase 7:** `COMPLETE`  
**Migration HEAD:** `0011_nfe_operational_fiscal_engine`  
**Git Working Tree:** `Clean`  

---

## 1. Visão Geral da Arquitetura

O LÉXORA (LXR) é uma plataforma inteligente e auditável para governança jurídica, fiscal e contábil no Brasil.

### Módulos Principais:
1. **Legal Brain:** Fonte autoritativa da legislação brasileira oficial (nós normativos, versões, evidências e artefatos brutos).
2. **Fiscal Brain & Decision Engine:** Classificação fiscal determinística, avaliação temporal de regras em `operation_date` e matemática financeira `Decimal` em política `ROUND_HALF_UP` (zero LLM em decisões fiscais).
3. **Fiscal Co-Pilot & Audit Dashboard:** Interface operacional web portável (`/dashboard`), assistente explicativo (`LLM = EXPLANATION ONLY`), máquina de estados de revisão humana, eventos de auditoria append-only (`ReviewEvent`), overrides imutáveis (`HumanOverride`) e motor de comparação (`FiscalDiffEngine`).
4. **Product Fiscal Classification & Tax Engine (FASE 6.5):** Perfis cadastrais fiscais de produtos (`FiscalProductProfile`), validação determinística de NCM/CEST/CST/CFOP, motor de apuração com memórias de cálculo auditáveis (`CalculationMemory`) e reprocessamento histórico não-destrutivo (`ReprocessingService`).
5. **Operational Fiscal Engine & NF-e Pipeline (FASE 7):** Pipeline operacional End-to-End para cargas úteis XML de NF-e (`POST /api/v1/fiscal/nfe/analyze`), validação contra XXE, extração de fatos, apuração determinística de impostos (ICMS, ICMS-ST, DIFAL, FCP, IPI, PIS, COFINS, ISS), preservação de fatos originais vs decisões do sistema e 5 cenários Golden obliterantes.

---

## 2. Status dos Componentes

| Módulo / Fase | Status | Descrição |
| :--- | :--- | :--- |
| Fundação Jurídica (Fases 1–5) | `CLOSED` | Modelo canônico, temporalidade, proveniência e integridade relacional protegida. |
| Fase 6.1 (Hybrid Legal Retrieval) | `COMPLETE` | Busca híbrida PostgreSQL vector + FTS. |
| Fase 6.2 (Contextual Legal RAG) | `SEALED` | RAG contextual, Answer Guardrails e citação de proveniência. |
| Fase 6.3 (Fiscal Brain & Decision Engine) | `COMPLETE` | Motores tributários determinísticos com precisão Decimal. |
| Fase 6.4 (Fiscal Co-Pilot & Audit Dashboard) | `COMPLETE` | Interface web dashboard, Co-Pilot, workflow de revisão e audit trail. |
| Fase 6.5 (Fiscal Classification & Tax Engine) | `COMPLETE` | Perfis fiscais, memórias de cálculo auditáveis e reprocessamento. |
| Fase 7 (Operational Fiscal Engine & NF-e) | `COMPLETE` | Pipeline operacional NF-e XML End-to-End e 5 cenários Golden. |

---

## 3. Próximos Passos
- Inicialização da próxima fase sob demanda.
