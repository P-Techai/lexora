# LÉXORA — Estado Atual do Projeto

**Data da Última Atualização:** 2026-08-10  
**Marco Atual:** Marco 1: NEXUS FISCAL BR — FOUNDATION  
**Versão Atual:** `0.1.0-foundation`  
**Status do Projeto:** Fundação documental, arquitetural, governança de agentes, portas de abstração e suite de testes básicos concluídos.

---

# 1. Resumo do Progresso Recente

- **Estrutura de Repositório Criada:** Repositório organizado segundo princípios de Clean Architecture e separação estrita de responsabilidades.
- **Memória Permanente:** Documentação completa estabelecida em `docs/` (`PROJECT.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `CURRENT_STATE.md`, `HANDOFF.md`, `DECISIONS.md`, `CHANGELOG.md`).
- **Governança de Agentes:** Regras de atuação e workflows gravados em `.agents/rules/` e `.agents/workflows/`.
- **Especificações Técnicas:** Criadas especificações para o Domínio Jurídico, Motor Fiscal, Parser de NF-e e Reforma Tributária em `specs/`.
- **Abstrações de Infraestrutura (Ports):** Interfaces declaradas para `StorageProvider`, `DatabaseProvider`, `LLMProvider`, `EmbeddingProvider`, `RerankerProvider`, `QueueProvider` e `SearchProvider` em `src/application/ports/`.
- **Modelos de Domínio:** Entidades `LegalNode` (com vigência temporal `effective_from`/`effective_until`) e `TaxCalculation` (com memória auditável de cálculo).
- **Adaptadores Iniciais:** Criados adaptadores `LocalStorageProvider` e `MockLLMProvider` para execução de testes locais.
- **Ambiente Local:** Criado `pyproject.toml`, `requirements.txt`, `.env.example`, `.gitignore` e `infrastructure/docker-compose.yml`.
- **Testes Unitários:** Suite inicial em `tests/unit/test_domain.py` e `tests/unit/test_ports.py`.

---

# 2. Árvore de Diretórios do Projeto

```
lexora/
├── .agents/
│   ├── rules/
│   │   ├── 01_legal_truth.md
│   │   ├── 02_architecture_portability.md
│   │   ├── 03_calculation_determinism.md
│   │   └── 04_handoff_documentation.md
│   └── workflows/
│       ├── development.md
│       └── handoff.md
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CHANGELOG.md
│   ├── CURRENT_STATE.md
│   ├── DECISIONS.md
│   ├── HANDOFF.md
│   ├── PROJECT.md
│   └── ROADMAP.md
├── infrastructure/
│   ├── docker-compose.yml
│   └── README.md
├── specs/
│   ├── fiscal_engine_spec.md
│   ├── legal_domain_spec.md
│   ├── nfe_parsing_spec.md
│   └── reforma_tributaria_spec.md
├── src/
│   ├── application/
│   │   ├── ports/
│   │   │   ├── database_provider.py
│   │   │   ├── llm_provider.py
│   │   │   ├── retrieval_ports.py
│   │   │   └── storage_provider.py
│   │   └── use_cases/
│   ├── domain/
│   │   ├── entities/
│   │   │   ├── legal_node.py
│   │   │   └── tax_calculation.py
│   │   └── enums.py
│   ├── infrastructure/
│   │   └── adapters/
│   │       ├── local_storage.py
│   │       └── mock_llm.py
│   └── interfaces/
│       └── api/
│           └── main.py
├── tests/
│   └── unit/
│       ├── test_domain.py
│       └── test_ports.py
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

# 3. Decisões Arquiteturais Registradas

- **ADR-001:** Adopção de Clean Architecture com 4 camadas puras.
- **ADR-002:** Estratégia Free-Tier First com Supabase, Cloudflare R2 e Neon via Inversão de Dependências.
- **ADR-003:** Princípio da Verdade Jurídica — Proibição de uso de LLMs como fonte primária de legislação.
- **ADR-004:** Motor de Cálculo Determinístico com Registro de Memória Auditável.
- **ADR-005:** Recuperação Híbrida (Lexical + Vetorial) com Reordenamento por Hierarquia Jurídica.

---

# 4. Próximas Tarefas (Marco 2)

1. Implementar o schema SQLAlchemy e migrations Alembic para persistência de `LegalNode` no PostgreSQL (`pgvector`);
2. Desenvolver o pipeline de ingestão de normas primárias (download, hash, armazenamento raw, parser e estruturação);
3. Construir a validação automatizada de vigência e grafo de relações normativas (`AMENDS`, `REVOKES`, `REGULATES`).
