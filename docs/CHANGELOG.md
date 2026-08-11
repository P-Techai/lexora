# LÉXORA — Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/) e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

---

## [0.1.0-foundation] - 2026-08-10

### Adicionado
- **Estrutura de Repositório:** Criação da estrutura base de diretórios (`.agents/`, `docs/`, `specs/`, `infrastructure/`, `src/`, `tests/`).
- **Documentação de Memória Permanente:**
  - `docs/PROJECT.md`: Visão geral, sigla LXR, princípios e governança.
  - `docs/ARCHITECTURE.md`: Detalhamento da Clean Architecture em 4 camadas e diagramas de sequência.
  - `docs/ROADMAP.md`: Planejamento dos marcos 1 ao 6.
  - `docs/CURRENT_STATE.md`: Estado atual do repositório, árvore de arquivos e tarefas.
  - `docs/HANDOFF.md`: Guia de continuidade para agentes e desenvolvedores.
  - `docs/DECISIONS.md`: Registros de Decisão Arquitetural ADR-001 a ADR-005.
  - `docs/CHANGELOG.md`: Histórico de versões.
- **Regras e Workflows de IA:**
  - `.agents/rules/01_legal_truth.md`: Princípio da verdade jurídica.
  - `.agents/rules/02_architecture_portability.md`: Portabilidade e desacoplamento via Clean Architecture.
  - `.agents/rules/03_calculation_determinism.md`: Determinismo em cálculos tributários.
  - `.agents/rules/04_handoff_documentation.md`: Regra de atualização documental contínua.
  - `.agents/workflows/development.md`: Workflow de desenvolvimento passo a passo.
  - `.agents/workflows/handoff.md`: Procedimento e checklist de handoff.
- **Especificações de Domínio:**
  - `specs/legal_domain_spec.md`: Modelo hierárquico de nós legais e vigência.
  - `specs/fiscal_engine_spec.md`: Regras fiscais e memória auditável de cálculo.
  - `specs/nfe_parsing_spec.md`: Pipeline de ingestão de XML de NF-e e pontuação de confiança.
  - `specs/reforma_tributaria_spec.md`: Simulação do regime dual de transição tributária.
- **Infraestrutura & Configuração:**
  - `infrastructure/docker-compose.yml`: Stack PostgreSQL 16 + pgvector para desenvolvimento local.
  - `pyproject.toml` e `requirements.txt`: Dependências do ecossistema Python (FastAPI, Pydantic, SQLAlchemy, Alembic, pytest).
  - `.env.example`: Modelo limpo de variáveis de ambiente.
  - `.gitignore`: Proteção de dados sensíveis e arquivos temporários.
- **Código-Fonte Foundation:**
  - Modelos de Domínio (`LegalNode`, `TaxCalculation`, enums jurídicos/fiscais).
  - Interfaces/Portas Abstratas (`StorageProvider`, `DatabaseProvider`, `LLMProvider`, `EmbeddingProvider`, `RerankerProvider`, `QueueProvider`, `SearchProvider`).
  - Adaptadores Iniciais (`LocalStorageProvider`, `MockLLMProvider`).
  - API Skeleton com FastAPI e healthcheck endpoint.
- **Testes Unitários:**
  - `tests/unit/test_domain.py`: Testes de vigência temporal e cálculo auditável.
  - `tests/unit/test_ports.py`: Testes de conformidade das portas de abstração.
