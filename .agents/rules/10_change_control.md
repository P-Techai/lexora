# Regra de Agente: 10 — Protocolo de Controle de Mudança (Change Control Pipeline)

---

# Fluxo Obrigatório para Alterações Estruturais

```
[1. PROPOSTA DE MUDANÇA] ──> [2. ANÁLISE DE IMPACTO] ──> [3. VERIFICAÇÃO DE COMPATIBILIDADE]
                                                                        │
[7. HANDOFF] <── [6. DOCUMENTAÇÃO] <── [5. TESTES] <── [4. IMPLEMENTAÇÃO / ADR] <──┘
```

1. **Proposta de Mudança:** Toda alteração em modelos de dados ou abstrações deve ter seu impacto mapeado.
2. **Compatibilidade com Invariantes:** Nenhuma mudança pode violar as regras de 4 camadas da Clean Architecture ou o determinismo aritmético fiscal.
3. **ADR Obrigatória:** Se uma decisão anterior for alterada ou um novo conceito for introduzido, registrar imediatamente um ADR em `docs/adr/`.
