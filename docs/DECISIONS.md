# LÉXORA — Registro de Decisões Arquiteturais (ADRs)

Este documento registra as decisões de arquitetura e design tomadas no projeto **LÉXORA (LXR)**, seu contexto, consequências e justificativas.

---

## ADR-001: Arquitetura Limpa (Clean Architecture) em 4 Camadas Puras

**Status:** Aprovado  
**Data:** 2026-08-10  
**Contexto:** O LÉXORA é uma plataforma de software de longo prazo que lidará com alta complexidade de domínio (legislação brasileira, regras fiscais e regras contábeis) e necessita ser facilmente testável e evolutiva.

**Decisão:** Adotar a Clean Architecture estruturada em 4 camadas isoladas:
1. `src/domain/`: Entidades puras, Value Objects e regras de negócio.
2. `src/application/`: Casos de uso e especificações de interfaces (Ports).
3. `src/infrastructure/`: Adaptadores concretos (bancos de dados, storage, LLMs, APIs).
4. `src/interfaces/`: API FastAPI, comandos CLI e controladores.

**Consequências:**
- Regras de domínio e lógica de negócio completamente isoladas de bibliotecas e frameworks de I/O.
- Testes unitários do domínio não exigem conexão de rede ou banco de dados ativo.
- Curva inicial de boilerplate ligeiramente maior, compensada por manutenção e portabilidade sustentáveis a longo prazo.

---

## ADR-002: Estratégia Vendor-Agnostic baseada em Free-Tier First

**Status:** Aprovado  
**Data:** 2026-08-10  
**Contexto:** A infraestrutura inicial deve rodar prioritariamente em serviços gratuitos (Supabase, Cloudflare R2/Workers, Neon), mas deve migrar posteriormente para infraestrutura paga ou privada sem reconstrução do código.

**Decisão:** Criar portas abstratas (`StorageProvider`, `DatabaseProvider`, `LLMProvider`, `EmbeddingProvider`, `RerankerProvider`, `QueueProvider`, `SearchProvider`) na camada `application/ports/`. Nenhuma classe do domínio ou caso de uso poderá importar SDKs proprietários (como `boto3`, `google-genai`, `openai`, `supabase-py`).

**Consequências:**
- Troca de provedores realizada 100% via configuração e injeção de adaptadores na camada `infrastructure/`.
- Risco zero de aprisionamento tecnológico (Vendor Lock-In).

---

## ADR-003: Princípio da Verdade Jurídica e Guardrails para LLMs

**Status:** Aprovado  
**Data:** 2026-08-10  
**Contexto:** Modelos de Linguagem (LLMs) tendem a apresentar alucinações em citação de leis, artigos e incisos, o que é inaceitável em um software jurídico-tributário profissional.

**Decisão:**
- O LLM **NUNCA** é a fonte da verdade jurídica ou fiscal.
- A fundamentação jurídica deve provir unicamente de dispositivos normativos canônicos cadastrados, versionados e validados temporalmente (`LegalNode`).
- Toda resposta gerada deve vincular cada afirmação jurídica ao identificador único da norma, artigo, parágrafo, inciso e fonte oficial primária.

**Consequências:**
- LLM restrito às funções de extração de dados, interpretação semântica assistida e síntese de linguagem natural.
- Garantia de auditabilidade e rastreabilidade total do conhecimento normativo.

---

## ADR-004: Motor de Cálculo Tributário Determinístico Auditável

**Status:** Aprovado  
**Data:** 2026-08-10  
**Contexto:** Cálculos de impostos (ICMS, PIS, COFINS, ISS, IPI, CBS, IBS, IS) exigem precisão matemática exata e conformidade estrita com alíquotas, bases de cálculo, reduções e regimes de tributação.

**Decisão:**
- Cálculos tributários **JAMAIS** serão executados por prompts ou código gerado dinamicamente por LLMs.
- Implementação de um motor de cálculo determinístico puro na linguagem base (Python), utilizando alta precisão numérica (`Decimal`).
- Cada cálculo gera obrigatoriamente um registro auditável `TaxCalculationLog` contendo: entradas, fórmula aplicada, versão da regra fiscal, fundamentação legal e resultado.

**Consequências:**
- Isenção total de erros de arredondamento ou inconsistências em cálculos financeiros.
- Memória de cálculo 100% reproduzível e auditável para contabilidade e fiscalização.

---

## ADR-005: RAG Híbrido com Reordenamento por Hierarquia Jurídica

**Status:** Aprovado  
**Data:** 2026-08-10  
**Contexto:** Legislação possui especificidades estruturais como hierarquia de normas (Constituição > Lei Complementar > Lei Ordinária > Decreto > Instrução Normativa), temporalidade (revogação e alteração) e especialidade.

**Decisão:** O pipeline de RAG (Recuperação de Conhecimento) utilizará:
1. Busca Lexical (BM25) para correspondência exata de termos legais, números de artigos e NCMs.
2. Busca Vetorial (`pgvector`) para alinhamento semântico de conceitos jurídicos.
3. Filtro Temporal estrito pela data da operação fiscal (`effective_from <= date <= effective_until`).
4. Reordenamento Jurídico (Legal Reranking) respeitando hierarquia, especialidade e vigência da norma.

**Consequências:**
- Respostas imunes a artigos revogados ou desatualizados na data da operação fiscal consultada.
