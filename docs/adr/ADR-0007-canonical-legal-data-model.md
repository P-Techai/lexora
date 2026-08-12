# ADR-0007: Modelo Jurídico Canônico e Isolamento Estrito Domínio/ORM

## Context
O LÉXORA necessita armazenar a legislação brasileira com total rastreabilidade documental, controle temporal de vigência, ordenamento estrutural e proveniência de evidências sem depender de representações voláteis de bancos vetoriais ou SDKs de ORM no domínio.

## Problem
Evitar a perda da estrutura original das normas (Artigo -> Parágrafo -> Inciso), evitar sobrescrever versões históricas e evitar acoplar as entidades puras de domínio a bibliotecas de banco de dados (como SQLAlchemy).

## Options
1. **Representação Simples por Chunks + Embedding:** Armazenar partes arbitrárias de texto com vetores. (Inviável para raciocínio jurídico determinístico).
2. **Modelo Jurídico Canônico em 6 Camadas + Separador ORM:** Modelar `Source`, `LegalDocument`, `LegalVersion`, `LegalNode` (árvore), `LegalRelation` e `Evidence`, mantendo as entidades Pydantic do domínio 100% isoladas dos modelos SQLAlchemy.

## Decision
Adotar o Modelo Jurídico Canônico em 6 Camadas com isolamento estrito entre Domínio e ORM:
- O conhecimento estruturado é a fonte primária da verdade. Embeddings são dados derivados.
- Nenhuma classe em `src/domain/` pode importar SQLAlchemy, psycopg, asyncpg ou drivers.
- O ordenamento ordinal dentro dos nós pai é garantido pelo campo `position`.
- A vigência temporal é avaliada por `effective_from` e `effective_until`.

## Consequences
- Garantia de reprodução exata do texto original e auditabilidade histórica.
- Testabilidade unitária do domínio em milissegundos sem necessidade de banco ativo.

## Migration Strategy
Consolidado na versão v0.3.0-canonical-model.
