# Regra de Agente: 02 — Arquitetura Limpa e Portabilidade (Architecture & Portability Rule)

---

# 1. Isolamento em 4 Camadas

Todo código escrito no projeto **LÉXORA** deve respeitar rigorosamente a separação de responsabilidades em 4 camadas concêntricas:

1. `src/domain/`: Entidades puras, Value Objects e regras de negócio. Zero dependências externas de I/O ou frameworks.
2. `src/application/`: Casos de uso, orquestração e especificações de portas abstratas (Interfaces).
3. `src/infrastructure/`: Adaptadores concretos (SQLAlchemy, Cloudflare R2, Supabase, SDKs de LLM, Parsers XML).
4. `src/interfaces/`: Endpoints FastAPI, CLI, controllers e schemas de entrada/saída.

---

# 2. Proibição de Lock-in de Fornecedor (Free-Tier First)

- A infraestrutura inicial prioriza camadas gratuitas (Supabase, Cloudflare R2, Neon), mas a aplicação deve permitir migração para qualquer nuvem (AWS, GCP, Azure, On-Premises) alterando unicamente arquivos na camada `infrastructure/`.
- NUNCA importe SDKs proprietários (`boto3`, `google-genai`, `openai`, `supabase-py`, etc.) diretamente dentro do `domain/` ou `application/`.
- Sempre declare a porta abstrata em `src/application/ports/` e implemente o adaptador em `src/infrastructure/adapters/`.

---

# 3. Princípios de Design de Software

- **Modularidade:** Mantenha módulos pequenos e focados. Evite arquivos gigantes com múltiplas responsabilidades.
- **Dependency Inversion:** Módulos de alto nível não devem depender de módulos de baixo nível. Ambos devem depender de abstrações.
- **Testabilidade:** Todo código das camadas `domain` e `application` deve possuir cobertura por testes unitários determinísticos.
