# Regra de Agente: 04 — Documentação Permanente e Regra de Handoff (Handoff Rule)

---

# 1. O Repositório Git é a Memória Permanente

- O projeto **LÉXORA** não pode depender da memória da janela de contexto ou do chat do agente.
- Toda decisão técnica importante, mudança de estado, nova funcionalidade ou refatoração deve ser imediatamente registrada nos arquivos de documentação do repositório.

---

# 2. Arquivos de Documentação Obrigatórios

Toda sessão ou tarefa significativa deve manter atualizados:

1. `docs/PROJECT.md`: Visão e governança geral.
2. `docs/ARCHITECTURE.md`: Mudanças na estrutura ou abstrações de portas.
3. `docs/CURRENT_STATE.md`: Estado exato do repositório, árvore de diretórios e testes executados.
4. `docs/HANDOFF.md`: Instruções precisas para o próximo agente ou desenvolvedor assumir a sessão.
5. `docs/DECISIONS.md`: Registro de novas decisões arquiteturais (ADRs).
6. `docs/CHANGELOG.md`: Histórico de versões e marcos concluídos.

---

# 3. Proibição de Finalização Sem Handoff

> [!CRITICAL]
> **NUNCA DECLARE UMA TAREFA CONCLUÍDA SEM ATUALIZAR A DOCUMENTAÇÃO CORRESPONDENTE.**

Antes de encerrar o turno, o agente DEVE apresentar:
1. O que foi criado ou modificado;
2. Árvore de diretórios atualizada;
3. Decisões arquiteturais tomadas;
4. Testes executados e resultado;
5. Problemas ou pendências encontradas;
6. Próxima tarefa detalhada;
7. Atualização do `CURRENT_STATE.md` e `HANDOFF.md`.
