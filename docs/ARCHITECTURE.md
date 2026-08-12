# LÉXORA — Arquitetura do Sistema

Este documento detalha a arquitetura técnica do **LÉXORA (LXR)** em **Clean Architecture** (4 Camadas Concêntricas) e a separação conceitual entre **Legal Brain**, **Fiscal Brain** e **Decision Engine**.

---

# 1. As 4 Camadas da Clean Architecture

```
               +-------------------------------------------------+
               |              interfaces (API / CLI)            |
               |  +-------------------------------------------+  |
               |  |          infrastructure (Adapters)         |  |
               |  |  +-------------------------------------+  |  |
               |  |  |       application (Use Cases & Ports)|  |  |
               |  |  |  +-------------------------------+  |  |  |
               |  |  |  |        domain (Entities)      |  |  |  |
               |  |  |  +-------------------------------+  |  |  |
               |  |  +-------------------------------------+  |  |
               |  +-------------------------------------------+  |
               +-------------------------------------------------+
```

---

# 2. Separação Conceitual dos Domínios

### 1. LEGAL BRAIN (Cérebro Jurídico)
Guarda o conhecimento normativo-institucional oficial:
- Legislação primária e secundária (Constituição, Leis Complementares, Leis Ordinárias, Decretos, INs);
- Jurisprudência (STF, STJ, CARF), Soluções de Consulta, Pareceres;
- Estrutura canônica de dispositivos (`LegalNode`);
- Controle estrito de vigência temporal (`effective_from`, `effective_until`);
- Grafo de relações normativas (`AMENDS`, `REVOKES`, `REGULATES`);
- Hierarquia, competência constitucional e evidências.

### 2. FISCAL BRAIN (Cérebro Fiscal)
Guarda o conhecimento operacional e tributário:
- Cadastro de produtos, mercadorias e serviços;
- Tabela NCM, CEST, CST, CSOSN, CFOP;
- Regimes tributários (Simples Nacional, Lucro Presumido, Lucro Real, MEI);
- Regras fiscais operacionais estaduais/federais/municipais;
- Motor de cálculo tributário determinístico puro (`Decimal`);
- Geração da memória imutável de cálculo (`TaxMemoryLog`).

### 3. DECISION ENGINE (Motor de Decisão)
Componente orquestrador de síntese:
- Recebe fatos, contexto, dados do *Legal Brain* e do *Fiscal Brain*;
- Produz a decisão enquadrada, a justificativa e o fundamento legal;
- Atribui o Nível de Confiabilidade (`CERTEZA`, `PROVÁVEL`, `INCERTA`, `CONFLITANTE`, `NÃO ENCONTRADA`);
- Encaminha para Fila de Revisão Humana quando a evidência for insuficiente.

---

# 3. Níveis de Confiança das Fontes (Source Trust)

- **Nível 1 (Oficial Primária):** DOU/DOE/DOM, Planalto, Receita Federal, CONFAZ, STF, STJ, CARF. *(Prioridade máxima).*
- **Nível 2 (Institucional Secundária):** Secretarias de Fazenda estaduais/municipais.
- **Nível 3 (Técnica Confiável):** Manuais oficiais, IBPT, tabelas técnicas.
- **Nível 4 (Comunitária):** Artigos, blogs e fóruns técnicos. *(Auxilia descoberta; jamais substitui fonte oficial).*

---

# 4. Auditoria e Versionamento de Modelos de IA

Todas as execuções auditáveis de síntese gravam a tupla de rastreabilidade:
- `llm_model`
- `embedding_model`
- `prompt_version`
- `retrieval_version`
- `rule_version`
- `application_version`

---

# 5. Segregação: Legal Knowledge x Company Knowledge

- **`Legal Knowledge`:** Conhecimento normativo oficial global (inalterável por decisões de clientes).
- **`Company Knowledge`:** Regras operacionais, preferências e decisões de revisão específicas de um tenant.
- **Multi-tenancy:** Isolamento estrito por `tenant_id` com suporte a RLS (Row Level Security) e RBAC (Role-Based Access Control).
