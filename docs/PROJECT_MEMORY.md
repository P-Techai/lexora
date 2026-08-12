# LÉXORA PROJECT MEMORY

---

## Identity
- **Nome Oficial:** LÉXORA
- **Pronúncia:** LÉK-so-ra
- **Sigla / Technical Name:** `lexora` (LXR)
- **Posicionamento:** Inteligência jurídica, fiscal e tributária brasileira.
- **Princípio da Marca:** "Inteligência que encontra a base."
- **Princípio Operacional:** "A Léxora não inventa. Ela encontra, cruza, interpreta e demonstra."
- **Personalidade:** Técnica, objetiva, precisa, fundamentada, transparente, conservadora em decisões fiscais, auditável, profissional, clara e humilde diante da incerteza.

---

## Mission
Fornecer uma plataforma inteligente de conhecimento jurídico, contábil e tributário brasileiro que fundamenta rigorosamente todas as suas respostas com artigos, dispositivos e fontes oficiais primárias, garantindo previsibilidade, determinismo aritmético e total auditabilidade.

---

## Product Vision
Evoluir de uma fundação limpa para um sistema profissional capaz de consultar a legislação brasileira com fundamentação jurídica exata, respeitando a vigência temporal, a hierarquia de normas e a competência constitucional; classificar produtos e operações; interpretar XML de NF-e; calcular tributos de forma determinística; e simular o impacto da Reforma Tributária.

---

## Architecture
- **Padrão:** Clean Architecture (Arquitetura Limpa / Hexagonal) em 4 camadas concêntricas (`domain/`, `application/`, `infrastructure/`, `interfaces/`).
- **Desacoplamento:** Nenhuma dependência direta de SDKs proprietários ou serviços de nuvem no domínio interno. Inversão de dependência via **Ports & Adapters**.

---

## Legal Brain
Domínio responsável pela verdade jurídica normativo-institucional:
- Legislação primária e secundária (Constituição, Leis Complementares, Leis Ordinárias, Decretos, Instruções Normativas);
- Atos normativos, jurisprudência (STF, STJ, CARF), soluções de consulta e pareceres;
- Estruturação canônica em árvore de nós (`LegalNode`);
- Controle estrito de vigência temporal (`effective_from`, `effective_until`);
- Grafo de relações normativas (`AMENDS`, `REVOKES`, `REGULATES`, `REFERENCES`, etc.);
- Hierarquia, competência e resolução de conflitos normativos;
- Gestão de evidências e fontes primárias oficiais.

---

## Fiscal Brain
Domínio responsável pelo conhecimento operacional e regras fiscais:
- Produtos, mercadorias e serviços;
- Tabelas e classificações: NCM, CEST, CST, CSOSN, CFOP;
- Regimes tributários (Simples Nacional, Lucro Presumido, Lucro Real, MEI);
- Regras operacionais fiscais estaduais, federais e municipais;
- Motor de cálculo tributário determinístico (PIS, COFINS, ICMS, ISS, IPI, CBS, IBS, IS);
- Geração imutável de memória de cálculo auditável (`TaxMemoryLog`);
- Obrigações acessórias e códigos de receita de arrecadação (DARF).

---

## Decision Engine
Componente orquestrador de síntese e julgamento fiscal:
- **Entradas:** Recebe contexto da operação, fatos estruturados, fundamentação do *Legal Brain*, regras do *Fiscal Brain*, cálculos tributários e evidências.
- **Saídas:** Produz a decisão enquadrada, justificativa clara, fundamentação jurídica com link para fontes primárias, nível de confiança e indicação de ressalvas ou necessidade de revisão humana.

---

## Infrastructure
- **Padrão de Banco:** PostgreSQL como padrão universal (Supabase e Neon tratados como adaptadores de infraestrutura).
- **Free-Tier First Strategy:** Operação inicial em camada gratuita migrável:
  - **Supabase:** PostgreSQL + `pgvector` + Autenticação;
  - **Cloudflare R2:** Armazenamento de objetos sem custo de egress (S3-compatible);
  - **Neon:** PostgreSQL para ambientes auxiliares, branches e staging.
- **Evolução de Infraestrutura:** `FREE` → `GROWTH` → `PRODUCTION` → `SCALE` realizada exclusivamente alterando a camada `infrastructure/` e arquivos de configuração.

---

## Data Model
- **Dispositivo Jurídico (`LegalNode`):** Nó hierárquico com vigência temporal, hash de integridade e metadados de fonte oficial.
- **Relação Jurídica (`LegalRelation`):** Aresta direcionada do grafo normativo com evidência de alteração ou revogação.
- **Cálculo Tributário (`TaxCalculation` & `TaxMemoryLog`):** Registro financeiro com entradas, fórmulas, alíquotas, resultado e hash auditável.
- **Segregação de Conhecimento:** Separação estrita entre `Legal Knowledge` (legislação oficial global) e `Company Knowledge` (decisões operacionais da empresa).
- **Multi-Tenancy:** Isolamento por `tenant_id` preparado para RLS (Row Level Security) e RBAC (Role-Based Access Control).

---

## AI Policy
- **LLM não é Fonte de Verdade:** O LLM atua estritamente como interpretador, extrator e orquestrador de linguagem natural. Jamais gera texto normativo ou regras fiscais do nada.
- **LLM não é Calculadora:** Cálculos tributários são 100% determinísticos em Python puro.
- **Escala de Confiabilidade:**
  - `CERTEZA`: Dispositivo vigente correspondente com alíquota e fundamentação direta.
  - `PROVÁVEL`: Correspondência de alta qualidade com jurisprudência/orientação uniforme.
  - `INCERTA`: Legislação com lacuna ou ambiguidade documental.
  - `CONFLITANTE`: Normas divergentes entre competências ou vigências não resolvidas.
  - `NÃO ENCONTRADA`: Ausência de base legal cadastrada (encaminha para revisão).

---

## Security
- Princípio do Menor Privilégio, segregação de credenciais via `.env`, isolamento de dados por tenant, logs de auditoria de acessos e decisões, conformidade com a LGPD (minimização e retenção configurável).

---

## Current Phase
**FASE 0 — Constituição e Fundação** (Concluída).

---

## Completed Milestones
- **Marco 1 / Fase 0:** `NEXUS FISCAL BR — FOUNDATION & CONSTITUTION`
  - Estrutura base de diretórios e projeto Python estabelecida.
  - Memória permanente, especificações de domínio e governança de agentes criadas.
  - Portas e adaptadores iniciais desenvolvidos com suite de testes unitários passando.

---

## Pending Milestones
- **Fases 1 a 15** do Roadmap oficial (Fase 1: Infraestrutura; Fase 2: Modelo Jurídico; Fase 3: Ingestão Oficial...).

---

## Critical Decisions
- **ADR-0001:** Clean Architecture em 4 Camadas.
- **ADR-0002:** Inversão de Dependências e Estratégia Free-Tier First.
- **ADR-0003:** Princípio da Verdade Jurídica e Guardrails para LLMs.
- **ADR-0004:** Motor de Cálculo Tributário Determinístico Auditável.
- **ADR-0005:** RAG Híbrido com Reordenamento por Hierarquia Jurídica.
- **ADR-0006:** Separação entre Legal Brain, Fiscal Brain e Decision Engine.

---

## Known Risks
- **Instabilidade em Fontes Governamentais:** Mudanças de layout ou indisponibilidade nos portais oficiais (Planalto/Receita Federal). *Mitigação:* Armazenar cópia *raw* com hash no Cloudflare R2 antes do parsing.
- **Conflitos de Vigência:** Leis estaduais/municipais divergentes. *Mitigação:* Matriz rigorosa de competência e nível de confiabilidade `CONFLITANTE` direcionando para Revisão Humana.

---

## Next Action
Iniciar a **FASE 1: Infraestrutura**, configurando os schemas ORM SQLAlchemy para o PostgreSQL (`pgvector`) e migrations do Alembic.
