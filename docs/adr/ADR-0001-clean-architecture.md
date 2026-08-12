# ADR-0001: Clean Architecture em 4 Camadas Puras

## Context
O **LÉXORA** é uma plataforma de software de longo prazo projetada para lidar com a alta complexidade do sistema jurídico, contábil e tributário brasileiro. O sistema exige facilidade de manutenção, testabilidade isolada e evolução contínua sem acoplamento a frameworks web ou bibliotecas de terceiros.

## Problem
Evitar monólitos desorganizados, misturas de lógica de banco de dados dentro de rotas de API ou regras de negócio espalhadas por templates e controladores.

## Options
1. **Arquitetura Tradicional MVC / Django-style:** Rápida para protótipos, porém acopla o modelo de dados ORM ao domínio de negócio.
2. **Clean Architecture (Arquitetura Limpa / Hexagonal):** Separação estrita em camadas concêntricas com inversão de dependências.

## Decision
Adotar Clean Architecture estruturada em 4 camadas concêntricas:
- `src/domain/`: Entidades puras, Value Objects e regras de negócio.
- `src/application/`: Casos de uso e portas de abstração (Interfaces).
- `src/infrastructure/`: Adaptadores concretos (SQLAlchemy, Cloudflare R2, LLMs).
- `src/interfaces/`: Endpoints FastAPI e controladores.

## Consequences
- Regras de domínio 100% isoladas de I/O e testáveis em ambiente local sem banco ativo.
- Leve sobretaxa inicial de arquivos/interfaces (boilerplate), amplamente compensada pela sustentabilidade do projeto.

## Migration Strategy
Não se aplica. Decisão fundacional desde a versão v0.1.0.
