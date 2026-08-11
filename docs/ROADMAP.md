# LÉXORA — Roadmap do Projeto

O desenvolvimento do **LÉXORA (LXR)** é organizado em marcos incrementais. Cada marco deve entregar um conjunto funcional completo com testes e documentação atualizada.

---

# Marco 1: NEXUS FISCAL BR — FOUNDATION (Em Execução)
**Objetivo:** Estabelecer a fundação documental, governança de agentes, arquitetura modular de software e infraestrutura inicial plugável.

- [x] Estrutura de diretórios organizada (`.agents/`, `docs/`, `specs/`, `infrastructure/`, `src/`, `tests/`);
- [x] Memória permanente criada (`PROJECT.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `CURRENT_STATE.md`, `HANDOFF.md`, `DECISIONS.md`, `CHANGELOG.md`);
- [x] Regras e workflows de governança para agentes de IA (`.agents/rules/`, `.agents/workflows/`);
- [x] Especificações técnicas dos domínios (`specs/`);
- [x] Abstrações de infraestrutura (`StorageProvider`, `DatabaseProvider`, `LLMProvider`, `RetrievalPorts`);
- [x] Implementação inicial de modelos de domínio (`LegalNode`, `TaxCalculation`);
- [x] Setup do ambiente local (`docker-compose.yml`, `pyproject.toml`, `requirements.txt`, `.env.example`);
- [x] Suite de testes unitários iniciais passando.

---

# Marco 2: INGESTÃO E VERSIONAMENTO JURÍDICO
**Objetivo:** Construir o pipeline de ingestão e estruturação canônica de legislação com controle de vigência.

- [ ] Pipeline de Ingestão: `DISCOVERY` → `DOWNLOAD` → `HASH` → `RAW_STORAGE` → `PARSER` → `NORMALIZATION` → `STRUCTURE` → `RELATIONS` → `EMBEDDINGS` → `VALIDATION` → `PUBLICATION`;
- [ ] Parsers para legislação federal (Constituição, Código Tributário Nacional, Leis Complementares, Leis Ordinárias);
- [ ] Grafo de Relações Normativas (`AMENDS`, `REVOKES`, `REGULATES`, `REFERENCES`);
- [ ] Tabela de versionamento temporal (`effective_from`, `effective_until`).

---

# Marco 3: RETRIEVAL JURÍDICO HÍBRIDO (RAG FISCAL)
**Objetivo:** Implementar o mecanismo de recuperação de conhecimento normativo com fundamentação legal rastreável.

- [ ] Engine de busca híbrida: Busca Lexical (BM25) + Busca Vetorial (`pgvector`);
- [ ] Filtro temporal obrigatório por data da operação fiscal;
- [ ] Reordenador hierárquico (Legal Reranker);
- [ ] Estruturador de respostas jurídicas (Conclusão, Base Legal, Interpretação, Vigência, Ressalvas, Fontes).

---

# Marco 4: MOTOR FISCAL E CÁLCULO DETERMINÍSTICO
**Objetivo:** Desenvolver o enquadramento de regras fiscais e o motor de cálculo tributário de alta precisão.

- [ ] Mapeamento determinístico de NCM, CEST, CST, CSOSN, CFOP;
- [ ] Motor de cálculo para ICMS, IPI, PIS, COFINS, ISS;
- [ ] Geração de memória de cálculo detalhada (`TaxCalculationLog`);
- [ ] Identificação de Códigos de Receita de Arrecadação (DARF).

---

# Marco 5: PARSER DE NF-e E REVISÃO HUMANA
**Objetivo:** Leitura de XMLs fiscais e roteamento inteligente para auditoria/revisão humana.

- [ ] Parser e validador de XML de NF-e;
- [ ] Algoritmo de Pontuação de Confiança (Confidence Score) baseado em evidências jurídicas e integridade de dados;
- [ ] Fila de Revisão Humana (Human Review Queue) com segregação de conhecimento corporativo (`Company Knowledge`) vs. conhecimento legal (`Legal Knowledge`).

---

# Marco 6: MÓDULO DA REFORMA TRIBUTÁRIA
**Objetivo:** Suporte ao regime dual de transição da Reforma Tributária brasileira.

- [ ] Modelo de dados para CBS, IBS e Imposto Seletivo (IS);
- [ ] Cronograma de transição de alíquotas e aproveitamento de créditos;
- [ ] Simulação de cenários: "Como é hoje" vs. "Como será na data X".
