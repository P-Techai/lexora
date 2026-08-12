# Regra de Agente: 08 — Segurança e Limites em Modo AUTO-ACCEPT

---

# 1. Princípios Invioláveis do Modo AUTO-ACCEPT

1. **AUTO-ACCEPT NÃO EQUIVALE A AUTORIZAÇÃO ARQUITETURAL:** O modo AUTO-ACCEPT do ambiente de agente automatiza a aprovação de execuções de plano, mas jamais autoriza desviar dos princípios e ADRs congelados do projeto LÉXORA.
2. **Proibição de Scope Creep:** Nunca implemente funcionalidades fora do escopo da fase ativa.
3. **Decisões Críticas Exigem ADR:** Nenhuma decisão arquitetural pode ser tomada silenciosamente sem a criação prévia de um arquivo de decisão em `docs/adr/`.
4. **LLM não é Autoridade Jurídica:** Proibido permitir que modelos de linguagem alterem a Verdade Jurídica (`Legal Truth`) diretamente sem evidência primária e validação determinística.
5. **Nenhum Fornecedor Pago ou Novo Banco:** Proibido introduzir Redis, Kafka, Elasticsearch, microserviços ou bancos vetoriais proprietários pagos.
