# LÉXORA — Protocolo Operacional de Agentes (AGENT_PROTOCOL.md)

Este documento estabelece o **Protocolo Obrigatório** para qualquer agente de inteligência artificial ou desenvolvedor humano que atuar no repositório do **LÉXORA (LXR)**.

---

# 1. O Princípio da Memória Permanente

> [!CRITICAL]
> **O REPOSITÓRIO GIT É A MEMÓRIA PERMANENTE DA LÉXORA.**
> A janela de contexto com o agente é estritamente temporária. Todo conhecimento arquitetural, decisão técnica, modelo de dados ou especificação DEVE obrigatoriamente existir em arquivos no repositório. Nunca deixe uma decisão relevante apenas no chat.

---

# 2. Ciclo de Vida Obrigatório de uma Tarefa

Qualquer agente deve seguir a sequência invariável de 10 passos:

```
[1. START] ──> [2. READ CONTEXT] ──> [3. INSPECT CODE] ──> [4. PLAN] ──> [5. IMPLEMENT]
                                                                                │
[10. HANDOFF] <── [9. UPDATE STATE] <── [8. REVIEW] <── [7. TEST] <─────────────┘
```

---

# 3. START PROTOCOL (Procedimento de Início)

Antes de modificar qualquer linha de código ou criar novos arquivos, você **DEVE** obrigatoriamente ler:

1. [README.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/README.md) — Visão geral e comandos rápidos;
2. [docs/PROJECT.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/PROJECT.md) — Visão de produto e princípios da marca;
3. [docs/PROJECT_MEMORY.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/PROJECT_MEMORY.md) — Memória condensada do repositório;
4. [docs/CURRENT_STATE.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/CURRENT_STATE.md) — Estado atual dos arquivos e progresso;
5. [docs/HANDOFF.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/HANDOFF.md) — Instruções deixadas pelo último agente;
6. [docs/DECISIONS.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/DECISIONS.md) e [docs/adr/](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/adr/) — Registros de decisão arquitetural (ADRs);
7. [docs/ARCHITECTURE.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/ARCHITECTURE.md) — Camadas de código e boundaries de domínio;
8. As regras ativas em [.agents/rules/](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/.agents/rules/);
9. Inspecione o código existente em `src/` e a suite de testes em `tests/`.

---

# 4. IMPLEMENTATION RULES (Regras Durante a Execução)

- **Regra de Não-Destruição:** Nunca apague código, documentação, migrations ou testes existentes sem justificativa explícita e registro de decisão (ADR).
- **Clean Architecture:** Mantenha a lógica de domínio em `src/domain/` completamente isolada de I/O. Defina portas em `src/application/ports/` e adapte em `src/infrastructure/adapters/`.
- **Determinismo:** Cálculos tributários devem ser 100% determinísticos em código Python (`Decimal`).
- **Verdade Jurídica:** Nunca permita que o LLM invente texto normativo ou alíquotas.

---

# 5. END PROTOCOL (Procedimento de Encerramento)

Ao concluir uma tarefa:

1. **Executar Testes:** Garanta que a suite de testes passa integralmente (`pytest`).
2. **Revisar Alterações:** Verifique a limpeza do código e padrões de formatação.
3. **Atualizar Memória Permanente:**
   - Atualize `docs/CHANGELOG.md` com a versão/modificação realizada;
   - Atualize `docs/CURRENT_STATE.md` com a nova árvore de diretórios e estado;
   - Atualize `docs/HANDOFF.md` com a próxima tarefa explícita;
   - Registre novos ADRs em `docs/adr/` e `docs/DECISIONS.md` se houver mudança de arquitetura;
   - Atualize `docs/PROJECT_MEMORY.md` se houver alteração estrutural relevante.
4. **Apresentar Relatório de Handoff:** Apresente o resumo final contendo:
   - O que foi criado/modificado;
   - Árvore de diretórios;
   - Decisões tomadas;
   - Testes executados;
   - Problemas encontrados;
   - Próxima tarefa prioritária.
