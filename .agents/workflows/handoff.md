# Workflow: Protocolo de Encerramento e Handoff (Handoff Workflow)

Este workflow especifica o procedimento obrigatório no final de cada sessão de trabalho.

---

# Checklist de Encerramento

1. **Testes Automatizados:**
   - Execute a suite de testes: `pytest`
   - Garanta 100% de passagem sem regressão.

2. **Atualização da Memória Permanente:**
   - Atualizar `docs/CHANGELOG.md` com a nova versão/alteração;
   - Atualizar `docs/CURRENT_STATE.md` com a árvore atualizada e progresso real;
   - Atualizar `docs/HANDOFF.md` com o próximo passo prioritário;
   - Se houver decisão arquitetural, registrar ADR em `docs/adr/` e atualizar `docs/DECISIONS.md`;
   - Se houver mudança estrutural relevante, atualizar `docs/PROJECT_MEMORY.md`.

3. **Relatório de Handoff para o Usuário:**
   Apresente a entrega contendo os 8 itens obrigatórios:
   1. O que foi criado;
   2. Árvore de diretórios;
   3. Decisões arquiteturais;
   4. Testes executados;
   5. Problemas encontrados;
   6. Próxima tarefa;
   7. Atualização do `CURRENT_STATE.md`;
   8. Atualização do `HANDOFF.md`.
