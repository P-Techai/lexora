# ADR-0002: Portabilidade de Provedores e Estratégia Free-Tier First

## Context
O LÉXORA deve iniciar operando em infraestrutura gratuita (Supabase, Cloudflare R2, Neon) sem contudo prender a aplicação a APIs proprietárias de nenhum fornecedor específico.

## Problem
Evitar o aprisionamento tecnológico (*Vendor Lock-In*) ao utilizar ofertas gratuitas de nuvem.

## Options
1. **Utilizar SDKs Proprietários Diretamente:** Usar SDKs do Supabase ou Cloudflare em todas as partes do código. (Alto risco de lock-in).
2. **Abstração por Interfaces (Ports & Adapters):** Declarar portas genéricas na camada `application/ports/` e implementar adaptadores na camada `infrastructure/adapters/`.

## Decision
Adotar Abstração por Interfaces (*Ports & Adapters*).
- O padrão de banco é PostgreSQL (Supabase e Neon são apenas provedores).
- Todas as dependências externas são injetadas através de adaptadores (`DatabaseProvider`, `StorageProvider`, `LLMProvider`, etc.).
- A progressão de infraestrutura segue o ciclo: `FREE` → `GROWTH` → `PRODUCTION` → `SCALE`.

## Consequences
- A troca de infraestrutura (ex.: de Cloudflare R2 para AWS S3 ou de Supabase para PostgreSQL *on-premises*) exige alterações exclusivamente na camada `infrastructure/`.
- Nenhuma classe do domínio ou caso de uso é alterada durante migrações.

## Migration Strategy
Troca efetuada via alteração de variáveis de ambiente (`.env`) e injeção do adaptador correspondente.
