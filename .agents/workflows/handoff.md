# Workflow de Handoff — LÉXORA

Este procedimento deve ser executado no final de cada sessão de trabalho ou entrega de marco.

---

# Checklist de Encerramento de Turno

1. **Auditoria de Arquivos Modificados:**
   - Liste todos os arquivos criados, alterados ou removidos no repositório.

2. **Validação de Testes:**
   - Execute o comando de teste: `pytest`
   - Confirme que não há falhas nem regressões.

3. **Atualização da Memória Permanente:**
   - `docs/CURRENT_STATE.md`: Atualizar árvore de diretórios, data e resumo do progresso.
   - `docs/HANDOFF.md`: Definir claramente o próximo marco e tarefa imediata.
   - `docs/DECISIONS.md`: Registrar quaisquer novas decisões tomadas durante a sessão.
   - `docs/CHANGELOG.md`: Atualizar notas de versão se houve nova funcionalidade relevante.

4. **Síntese de Handoff para o Usuário:**
   Apresentar o relatório contendo:
   1. O que foi criado/modificado;
   2. Árvore de diretórios;
   3. Decisões arquiteturais;
   4. Testes executados;
   5. Problemas encontrados;
   6. Próxima tarefa prioritária.
