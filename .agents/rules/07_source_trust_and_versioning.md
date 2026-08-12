# Regra de Agente: 07 — Níveis de Confiança da Fonte e Versionamento de IA

---

# 1. Níveis de Confiança das Fontes (Source Trust)

Toda fonte de informação integrada ao LÉXORA deve ser categorizada em uma das 4 camadas de confiança:

- **Nível 1 (Oficial Primária):** Diário Oficial da União/Estado/Município, Portal do Planalto, Receita Federal do Brasil, CONFAZ, STF, STJ, CARF. *(Prioridade máxima).*
- **Nível 2 (Institucional Secundária):** Secretarias estaduais de Fazenda, órgãos governamentais de segundo escalão.
- **Nível 3 (Técnica Confiável):** Manuais fiscais oficiais, tabelas IBPT, entidades de classe reconhecidas.
- **Nível 4 (Comunitária):** Artigos, blogs e fóruns técnicos. *(Permitido unicamente para descoberta inicial de contexto; jamais substitui fonte primária).*

---

# 2. Requisito de Versionamento de IA e Auditoria

Toda decisão ou resposta gerada com auxílio de modelos de IA deve registrar obrigatoriamente para fins de auditabilidade:

```json
{
  "llm_model": "gpt-4o / gemini-1.5-pro",
  "embedding_model": "text-embedding-3-small",
  "prompt_version": "v1.2.0",
  "retrieval_version": "v1.0.0",
  "rule_version": "hash-da-regra",
  "application_version": "0.2.0-constitution"
}
```

---

# 3. Segregação: Legal Knowledge vs. Company Knowledge

- Uma decisão de revisão humana ou ajuste operacional de uma empresa altera unicamente o `Company Knowledge`.
- Decisões operacionais **JAMAIS** alteram a base de legislação oficial global (`Legal Knowledge`).
