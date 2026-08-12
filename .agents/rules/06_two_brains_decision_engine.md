# Regra de Agente: 06 — Separação dos Dois Cérebros e Decision Engine

---

# 1. Os Dois Cérebros

O código do LÉXORA deve respeitar a divisão conceitual estrita entre os dois cérebros do sistema:

### LEGAL BRAIN (Cérebro Jurídico)
Guarda a verdade normativo-institucional oficial:
- Legislação primária e secundária;
- Jurisprudência, atos normativos, soluções de consulta;
- Dispositivos normativos hierárquicos (`LegalNode`);
- Controle temporal de vigência e grafo de relações normativas.

### FISCAL BRAIN (Cérebro Fiscal)
Guarda o conhecimento operacional e regras de enquadramento:
- Cadastro de produtos, NCM, CEST, CST, CSOSN, CFOP;
- Regimes tributários (Simples, Presumido, Real);
- Regras fiscais operacionais e motor de cálculo determinístico (`Decimal`).

---

# 2. Decision Engine (Motor de Decisão)

- O `Decision Engine` é o componente sintetizador.
- Ele recebe fatos, contexto, dados do *Legal Brain* e do *Fiscal Brain*, produzindo a decisão final com fundamentação, nível de confiança, ressalvas e indicação de revisão.
- **RAG NÃO É MOTOR FISCAL:** O RAG recupera conhecimento normativo; ele não decide autonomamente alíquotas ou enquadramentos fiscais sem passar pelo motor de regras e pelo contexto jurídico.
