# ADR-0009: Governança de Fontes, Proteção SSRF e Separação de RawArtifacts

## Context
A aquisição de documentos normativos exige governança rígida sobre as origens autorizadas e proteção proativa contra vulnerabilidades de rede (como SSRF), garantindo a preservação dos artefatos brutos capturados.

## Problem
Evitar que requisições HTTP arbitrárias acessem redes privadas, localhost ou endpoints de metadados de nuvem, e impedir a perda ou corrupção do conteúdo bruto original.

## Options
1. **Aquisição Direta sem Validação de URL:** Alto risco de SSRF e falta de governança.
2. **Registry de Fontes + Validador SSRF + Armazenamento de RawArtifacts:** Registro formal de fontes com allowlist de domínios, bloqueio estrito de IPs privados/localhost (`URLSecurityValidator`) e gravação independente de `RawArtifact` no `StorageProvider`.

## Decision
Adotar o Registry de Fontes com Proteção SSRF e Separação de RawArtifacts:
- Nenhuma URL é consultada sem pertencer à allowlist da fonte.
- IPs de loopback, redes privadas (`10.x`, `172.16-31.x`, `192.168.x`) e metadados (`169.254.169.254`) são bloqueados ativamente.
- Artefatos brutos são gravados com hash SHA-256 no `StorageProvider` antes de qualquer parsing.

## Consequences
- Imunidade contra Server-Side Request Forgery (SSRF) e rastreabilidade imutável de capturas.

## Migration Strategy
Consolidado na versão v0.5.0-acquisition-engine.
