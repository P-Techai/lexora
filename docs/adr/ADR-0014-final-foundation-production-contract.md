# ADR-0014: Selamento de Contratos de Produção e Fechamento Definitivo da Fundação

## Context
Após os prompts de hardening 06 a 07.2, realizou-se a reparação técnica e o selamento de produção dos contratos do LÉXORA (Prompt 07.3). Esta decisão registra a unificação da porta de aquisição, a validação de segurança SSRF por resolução DNS (A e AAAA), a leitura por streaming de chunks (64KB), a identidade lógica determinística dos nós e o alinhamento total de schemas relacionais e enums.

## Decision
1. **Contrato Único de Aquisição:** A porta `DocumentAcquisitionProvider` exige a assinatura única `acquire(request: AcquisitionRequest) -> AcquisitionResult`. Qualquer método legado `acquire_document` foi definitivamente eliminado.
2. **Leitura Incremental em Chunks de 64KB:** `HttpDocumentAcquisitionAdapter` realiza download streaming em blocos de 64KB, calculando o hash SHA-256 incrementalmente e abortando com `ArtifactTooLargeError` se o limite `max_bytes` for excedido durante a leitura (independente de `Content-Length`).
3. **Proteção SSRF com Resolução DNS (A/AAAA):** `URLSecurityValidator` resolve nomes de host via `socket.getaddrinfo` e valida todos os IPs resultantes contra faixas privadas, loopback (`127.x`, `::1`), link-local e metadata endpoints (`169.254.169.254`).
4. **Safe Redirect Handler:** `SafeRedirectHandler` restringe redirecionamentos a no máximo 5 hops, captura `redirect_chain`, proíbe o downgrade de HTTPS para HTTP e re-valida todas as URLs de destino contra regras SSRF e allowlists.
5. **Identidade Lógica Canônica (`logical_id`):** Nós normativos (`LegalNode`) possuem a propriedade `logical_id` derivada de `f"{legal_version_id}:{path}"` e hash canônico `DocumentHashCalculator.calculate_canonical_node_hash`, eliminando a participação de UUIDs aleatórios na identidade lógica da árvore.
6. **Alinhamento do Enum `ChangeStatus`:** `ChangeStatus.UPDATED` foi permanentemente substituído por `ChangeStatus.CHANGED`.
7. **Consistência Relacional:** O catálogo relacional PostgreSQL (Alembic `0005_phase5_normative_acts`) impõe FKs `RESTRICT` e restrições `UNIQUE` contra duplicações concorrentes.

## Consequences
- A fundação do LÉXORA encontra-se 100% selada, internamente consistente e testada.
- **Status da Fundação:** **`CLOSED`**
- **Status da FASE 6:** **`AUTHORIZED`**
