# LÉXORA — Guia de Infraestrutura e Provedores (Infrastructure & Free Tier Strategy)

Este guia descreve como rodar a infraestrutura do **LÉXORA (LXR)** em desenvolvimento local e como configurar os provedores em camada gratuita (Free Tier).

---

# 1. Desenvolvimento Local (Docker)

Suba a instância local do PostgreSQL 16 com extensão `pgvector`:

```bash
docker-compose up -d
```

String de conexão local por padrão:
`postgresql+asyncpg://lexora_user:lexora_password@localhost:5432/lexora_db`

---

# 2. Mapeamento de Camada Gratuita (Free Tier Strategy)

| Serviço de Infraestrutura | Provedor Gratuito Recomendado | Limites & Benefícios | Interface no LÉXORA (Porta) |
| :--- | :--- | :--- | :--- |
| **PostgreSQL + pgvector** | **Supabase** / **Neon** | Supabase: 500MB DB, pgvector habilitado.<br>Neon: 0.5 GiB storage, branching. | `DatabaseProvider` |
| **Object Storage (PDF/XML)** | **Cloudflare R2** | 10 GB/mês de armazenamento gratuito, 0 custos de egresso (zero egress fee). | `StorageProvider` |
| **LLM & Embeddings** | **Cloudflare Workers AI** / **OpenAI Free** / **Gemini** | Limites gratuitos diários para tarefas de extração e suporte. | `LLMProvider`, `EmbeddingProvider` |
| **Execução Serverless / Edge** | **Cloudflare Workers** | 100.000 requisições/dia gratuitas. | `interfaces/` |

---

# 3. Princípio de Migração sem Reconstrução

Como a aplicação se conecta a essas tecnologias exclusivamente por adaptadores da camada `infrastructure/adapters/`, migrar de uma nuvem gratuita para uma infraestrutura paga (ex.: AWS RDS, S3, ECS, OpenAI Enterprise) exige unicamente:

1. Atualizar as variáveis de ambiente em `.env`;
2. Instalar o driver/SDK do provedor na infraestrutura;
3. Injetar a nova classe de adaptador no container de dependências.

Nenhuma linha do código de domínio ou de regras fiscais é alterada.
