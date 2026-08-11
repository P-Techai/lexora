# LÉXORA — Handoff do Projeto

Este documento instrui desenvolvedores e agentes de IA sobre como assumir a continuidade do projeto **LÉXORA (LXR)** sem perda de contexto ou decisões arquiteturais.

---

# 1. Instruções para Início de Turno / Nova Sessão

Antes de realizar qualquer modificação no código:

1. **Leia a memória permanente:**
   - [PROJECT.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/PROJECT.md) — Visão e Princípios;
   - [ARCHITECTURE.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/ARCHITECTURE.md) — Arquitetura de 4 camadas;
   - [CURRENT_STATE.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/CURRENT_STATE.md) — Estado atual do projeto;
   - [DECISIONS.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/DECISIONS.md) — Decisões arquiteturais registradas;
   - [ROADMAP.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/ROADMAP.md) — Marcos e entregas.

2. **Verifique as regras do agente:**
   - [.agents/rules/01_legal_truth.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/.agents/rules/01_legal_truth.md)
   - [.agents/rules/02_architecture_portability.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/.agents/rules/02_architecture_portability.md)
   - [.agents/rules/03_calculation_determinism.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/.agents/rules/03_calculation_determinism.md)
   - [.agents/rules/04_handoff_documentation.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/.agents/rules/04_handoff_documentation.md)

3. **Verifique a saúde do ambiente:**
   - Execute a suite de testes unitários: `pytest`
   - Certifique-se de que a árvore de diretórios está íntegra.

---

# 2. Checklist Obrigatório de Finalização de Tarefa

Ao concluir qualquer tarefa significativa:

- [ ] **Testes:** Garanta que todos os testes unitários e de integração existentes continuam passando sem regressão;
- [ ] **Novos Testes:** Adicione testes automatizados para a funcionalidade criada;
- [ ] **Documentação:** Atualize `docs/CURRENT_STATE.md` com a árvore atualizada, novos arquivos e testes executados;
- [ ] **Decisões:** Se uma decisão arquitetural foi tomada, registe um novo ADR em `docs/DECISIONS.md`;
- [ ] **Histórico:** Registre a alteração em `docs/CHANGELOG.md`;
- [ ] **Handoff:** Atualize este arquivo (`docs/HANDOFF.md`) com a indicação exata da próxima tarefa.

---

# 3. Próximo Passo Prioritário

**Marco Atual:** Marco 2 — Ingestão e Versionamento Jurídico.  
**Tarefa Imediata:** 
1. Criar o modelo ORM SQLAlchemy (`src/infrastructure/db/models/legal_node_model.py`) correspondente à entidade de domínio `LegalNode`;
2. Configurar a migration Alembic inicial para PostgreSQL com extensão `pgvector`;
3. Desenvolver o parser de ingestão para normas primárias federais (ex.: Constituição Federal / Código Tributário Nacional).
