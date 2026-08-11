# LÉXORA — Visão Geral do Projeto

**Nome Oficial:** LÉXORA  
**Sigla:** LXR  
**Nome Técnico:** `lexora`  
**Descrição:** Plataforma inteligente de conhecimento jurídico, tributário e contábil brasileiro.

---

# 1. Visão e Filosofia

O LÉXORA não é um protótipo descartável nem um simples chatbot. É uma plataforma modular de software de longo prazo capaz de:

1. Consultar legislação brasileira com fundamentação jurídica exata;
2. Realizar cruzamentos entre normas;
3. Respeitar hierarquia jurídica, competência, especialidade e vigência temporal;
4. Responder sempre apontando artigos, dispositivos e fontes oficiais primárias;
5. Acompanhar alterações legislativas mantendo histórico de versões;
6. Classificar produtos e operações fiscais;
7. Interpretar arquivos NF-e (XML);
8. Sugerir NCM, CEST, CST, CSOSN e CFOP;
9. Calcular tributos de forma determinística;
10. Gerar memória de cálculo auditável;
11. Identificar códigos de receita;
12. Permitir revisão humana estruturada;
13. Aprender com decisões operacionais sem alterar a verdade jurídica;
14. Acompanhar e simular a Reforma Tributária (dualidade CBS/IBS/IS vs. PIS/COFINS/ICMS/ISS);
15. Operar com custo zero em infraestrutura gratuita (free-tier first) e migrar para infraestrutura paga sem reescrever o código.

---

# 2. Princípio Fundamental de Separação de Camadas

A arquitetura do LÉXORA proíbe misturar responsabilidades. Cada componente tem um propósito bem definido:

| Tecnologia | Responsabilidade |
| :--- | :--- |
| **RAG Híbrido** | Recuperação semântica e lexical de conhecimento normativo |
| **PostgreSQL** | Fatos estruturados, transações, dados cadastrais e logs auditáveis |
| **pgvector** | Armazenamento e busca por vetores de simetria semântica |
| **Legal Knowledge Graph** | Mapeamento de relações entre normas (altera, revoga, regulamenta, etc.) |
| **Rule Engine** | Tomada de decisão fiscal determinística |
| **Calculation Engine** | Motor de cálculo tributário financeiro de alta precisão |
| **LLM (Orquestrador)** | Interpretação de texto, extração de metadados, classificação assistida e síntese |
| **Human Review** | Exceções, ambiguidades e validações de alto impacto |

---

# 3. Regra de Ouro: A Verdade Jurídica

> [!CRITICAL]
> **O LLM NÃO É A FONTE DA VERDADE JURÍDICA OU FISCAL.**
> Nenhuma resposta do LLM pode ser considerada legislação. A verdade jurídica deve advir exclusivamente de:
> - Fontes oficiais primárias (Planalto, Receita Federal, CONFAZ, STF, STJ, CARF, etc.);
> - Dispositivo normativo canônico versionado;
> - Vigência temporal confirmada (`effective_from` e `effective_until`);
> - Relações normativas rastreáveis e justificativa de regra aplicada.

---

# 4. Infraestrutura e Portabilidade

- **Fase Inicial:** 100% hospedada em camadas gratuitas (Free Tier First):
  - **Supabase / Neon:** PostgreSQL + `pgvector` + Autenticação;
  - **Cloudflare:** R2 (storage compatível S3), Workers, DNS, CDN;
  - **Execução local/Docker:** Desenvolvimento e testes isolados.
- **Portabilidade Total:** Lógica de negócio 100% desacoplada de SDKs proprietários via Design Pattern **Ports & Adapters** (Clean Architecture / Hexagonal Architecture).

---

# 5. Organização do Repositório

```
lexora/
├── .agents/             # Regras e workflows de IA/Agentes
│   ├── rules/
│   └── workflows/
├── docs/                # Memória permanente do projeto
├── specs/               # Especificações técnicas de domínio
├── infrastructure/      # Docker, IaC e scripts de implantação
├── src/                 # Código-fonte da aplicação (Clean Architecture)
│   ├── domain/          # Entidades, Value Objects e Regras de Negócio
│   ├── application/     # Interfaces/Ports e Casos de Uso
│   ├── infrastructure/  # Adaptadores concretos (Supabase, R2, LLMs)
│   └── interfaces/      # APIs FastAPI e CLI
└── tests/               # Testes unitários, de integração e fixtures
```
