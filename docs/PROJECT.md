# LÉXORA — Visão Geral do Projeto

**Nome Oficial:** LÉXORA  
**Pronúncia:** LÉK-so-ra  
**Sigla:** LXR  
**Nome Técnico:** `lexora`  
**Posicionamento:** Inteligência jurídica, fiscal e tributária brasileira.

---

# 1. Princípios da Marca e Operacionais

- **Princípio da Marca:** "Inteligência que encontra a base."
- **Princípio Operacional:** "A Léxora não inventa. Ela encontra, cruza, interpreta e demonstra."

---

# 2. Personalidade da Léxora

A Léxora é uma plataforma profissional de conhecimento que atua com a seguinte personalidade:
- **Técnica, objetiva e precisa;**
- **Fundamentada em fontes oficiais primárias;**
- **Transparente e auditável;**
- **Conservadora em decisões fiscais;**
- **Humilde e clara diante da incerteza.**

A Léxora **NÃO** finge certeza, não inventa artigos/alíquotas/vigências e não substitui a revisão humana em casos de evidência insuficiente.

---

# 3. Princípio de Confiabilidade (Escala de 5 Níveis)

Toda informação relevante emitida pela Léxora é enquadrada em um dos 5 níveis:
1. `CERTEZA`: Dispositivo normativo vigente correspondente com fundamentação direta.
2. `PROVÁVEL`: Correspondência de alta qualidade sustentada por orientação oficial.
3. `INCERTA`: Legislação com lacuna ou ambiguidade documental identificada.
4. `CONFLITANTE`: Normas divergentes entre competências ou vigências não resolvidas.
5. `NÃO ENCONTRADA`: Ausência de base legal cadastrada (roteia para Revisão Humana).

---

# 4. Regra de Ouro: A Verdade Jurídica

> [!CRITICAL]
> **O LLM NÃO É A FONTE DA VERDADE JURÍDICA OU FISCAL.**
> A verdade jurídica provém exclusivamente de fontes oficiais primárias (Planalto, Receita Federal, CONFAZ, STF, STJ, CARF, etc.), dispositivos normativos canônicos versionados (`LegalNode`), controle estrito de vigência e relações normativas rastreáveis.

---

# 5. Estrutura em Dois Cérebros e Decision Engine

```
               +----------------------------------------+
               |             DECISION ENGINE            |
               | (Sintetizador & Julgamento de Certeza) |
               +-------------------+--------------------+
                                   |
         +-------------------------+-------------------------+
         |                                                   |
+--------v-------+                                  +--------v-------+
|   LEGAL BRAIN  |                                  |  FISCAL BRAIN  |
|  (Legislação,  |                                  |   (Produtos,   |
|   Vigência,    |                                  |   NCM, CST,    |
|   Hierarquia)  |                                  |   Cálculos)    |
+----------------+                                  +----------------+
```

---

# 6. Organização do Repositório

```
lexora/
├── .agents/             # Regras e workflows invioláveis de IA/Agentes
│   ├── rules/
│   └── workflows/
├── docs/                # Memória permanente condensada e ADRs
│   └── adr/
├── specs/               # Especificações técnicas dos domínios
├── infrastructure/      # Docker, IaC e estratégias de provedor
├── src/                 # Código-fonte da aplicação (Clean Architecture)
│   ├── domain/          # Entidades, Value Objects e Regras
│   ├── application/     # Ports (Interfaces) e Casos de Uso
│   ├── infrastructure/  # Adaptadores concretos (SQLAlchemy, Cloudflare, LLM)
│   └── interfaces/      # APIs FastAPI e CLI
└── tests/               # Suite de testes unitários e de integração
```
