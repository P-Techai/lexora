# LÉXORA — Roadmap Oficial do Projeto (Fases 0 a 15)

O desenvolvimento do **LÉXORA (LXR)** segue 16 fases estritas. É expressamente proibido antecipar fases sem que o modelo da fase anterior esteja consolidado.

---

# FASE 0: Constituição e Fundação
**Status:** [x] Concluída
- [x] Repositório estruturado em Clean Architecture;
- [x] Memória permanente criada (`PROJECT_MEMORY.md`, `AGENT_PROTOCOL.md`, `PROJECT.md`, `ARCHITECTURE.md`);
- [x] Diretório de ADRs estabelecido (`docs/adr/ADR-0001` a `ADR-0006`);
- [x] Regras de IA e workflows invioláveis em `.agents/`;
- [x] Especificações técnicas dos domínios em `specs/`;
- [x] Modelos purificados e portas de abstração em `src/`;
- [x] Suite de testes unitários básicos em `tests/`.

---

# FASE 1: Infraestrutura
**Status:** [ ] Próxima Fase
- [ ] Schema ORM SQLAlchemy para `legal_nodes` e `legal_relations` no PostgreSQL (`pgvector`);
- [ ] Migrations do Alembic configuradas;
- [ ] Configuração de adaptadores para Supabase, Cloudflare R2 e Neon;
- [ ] Pipeline de CI/CD via GitHub Actions.

---

# FASE 2: Modelo Jurídico
**Status:** [ ] Planejada
- [ ] Modelagem canônica dos tipos de norma e nós hierárquicos (`LegalNode`);
- [ ] Validações de integridade e calculadores de hash de documento.

---

# FASE 3: Ingestão Oficial
**Status:** [ ] Planejada
- [ ] Ingestão de fontes primárias oficiais (Planalto, Receita Federal, CONFAZ);
- [ ] Armazenamento *raw* no Cloudflare R2 com hash de integridade;
- [ ] Parsers de estrutura para Constituição, LCs e LOs.

---

# FASE 4: Versionamento e Vigência
**Status:** [ ] Planejada
- [ ] Controle temporal estrito (`effective_from`, `effective_until`);
- [ ] Grafo de relações normativas (`AMENDS`, `REVOKES`, `REGULATES`);
- [ ] Motor de consulta temporal por data da operação fiscal.

---

# FASE 5: RAG Híbrido
**Status:** [ ] Planejada
- [ ] Engine de busca híbrida: Busca Lexical (BM25) + Vetorial (`pgvector`);
- [ ] Filtro temporal obrigatório e reordenador por hierarquia jurídica (*Legal Reranker*).

---

# FASE 6: Legal Reasoning Engine
**Status:** [ ] Planejada
- [ ] Grafo de raciocínio jurídico e resolução de conflitos (Constituição > LC > LO > Decreto);
- [ ] Identificação automatizada de ambiguidades e lacunas normativas.

---

# FASE 7: Fiscal Rule Engine
**Status:** [ ] Planejada
- [ ] Enquadramento determinístico de NCM, CEST, CST, CSOSN e CFOP.

---

# FASE 8: NF-e / XML
**Status:** [ ] Planejada
- [ ] Pipeline de ingestão, validação de schema e extração de itens de XML de NF-e.

---

# FASE 9: Classificação Fiscal
**Status:** [ ] Planejada
- [ ] Algoritmo de Pontuação de Confiança (*Confidence Score*) e classificação assistida de produtos.

---

# FASE 10: Cálculos e Memória
**Status:** [ ] Planejada
- [ ] Motor de cálculo tributário determinístico puro (`Decimal`) com geração de `TaxMemoryLog` auditável.

---

# FASE 11: Human Review
**Status:** [ ] Planejada
- [ ] Fila de revisão humana para tratamento de exceções, ambiguidades e produtos complexos;
- [ ] Segregação de `Company Knowledge` vs. `Legal Knowledge`.

---

# FASE 12: Monitoramento Legislativo
**Status:** [ ] Planejada
- [ ] Acompanhamento de alterações no Diário Oficial e alertas de revogação/alteração.

---

# FASE 13: Reforma Tributária
**Status:** [ ] Planejada
- [ ] Suporte ao regime dual (CBS, IBS, IS vs PIS/COFINS/ICMS/ISS) e simulação de cenários de transição.

---

# FASE 14: Expansão Estadual
**Status:** [ ] Planejada
- [ ] Ingestão e regras específicas dos 27 estados e principais municípios brasileiros.

---

# FASE 15: Produção
**Status:** [ ] Planejada
- [ ] Endurecimento de segurança (RLS/RBAC), observabilidade, auditoria completa e escala de infraestrutura.
