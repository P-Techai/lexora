# Regra de Agente: 01 — Verdade Jurídica e Rastreadilidade (Legal Truth Rule)

> [!CRITICAL]
> **ESTA É UMA REGRA FUNDAMENTAL E INVIOLÁVEL DO PROJETO LÉXORA.**

---

# 1. Princípio da Verdade Jurídica

1. **O LLM NÃO É A FONTE DA VERDADE JURÍDICA OU FISCAL.**
2. O sistema jamais tratará uma resposta ou geração do LLM como texto normativo ou legislação válida.
3. A verdade jurídica reside exclusivamente em:
   - Fontes primárias oficiais (Diário Oficial da União, Planalto, Receita Federal, CONFAZ, STF, STJ, CARF, Secretarias de Fazenda);
   - Dispositivos normativos canônicos cadastrados na base de dados (`LegalNode`);
   - Controle temporal explícito de vigência (`effective_from` e `effective_until`);
   - Relações normativas rastreáveis (`AMENDS`, `REVOKES`, `REGULATES`).

---

# 2. Requisitos de Fundamentação Obrigatórios

Toda resposta jurídica ou fiscal relevante do sistema deve conseguir responder com evidência factual:

- Qual a norma aplicável? (Ex.: Lei Complementar nº 87/1996)
- Qual o artigo específico? (Ex.: Art. 3º)
- Qual o parágrafo / inciso / alínea / item? (Ex.: Inciso VIII)
- Qual a versão da norma vigente na data da operação fiscal?
- Qual a fonte oficial do documento?
- Qual a relação da norma com outros diplomas legais existentes?
- Qual a regra de conflito / hierarquia aplicada?
- Existe ambiguidade ou incerteza detectada?

---

# 3. Restrições Estritas para Agentes de IA

- **NUNCA** invente ou alucine citações de artigos, incisos ou alíneas.
- **NUNCA** crie regras tributárias "prováveis" sem respaldo normativo direto.
- **NUNCA** altere a verdade jurídica oficial com base em decisões humanas operacionais da empresa. Mantenha estritamente segregado `Legal Knowledge` de `Company Knowledge`.
- Se faltar evidência primária oficial, o sistema DEVE declarar **incerteza legal** ou emitir solicitação de **Revisão Humana**.
