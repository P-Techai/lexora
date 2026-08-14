# LÉXORA — Especificação de Ingestão e Parsing Seguro de NFe (NFe Parsing)

Este documento descreve a porta e adaptador de parsing de XMLs de Nota Fiscal Eletrônica (NFe) no **LÉXORA (LXR)**.

---

# 1. Medidas de Segurança Enforçadas (`SecureNFeParser`)

1. **Defesa contra XXE (XML External Entity):** O parser rejeita qualquer XML contendo declarações `<!DOCTYPE` ou `<!ENTITY`.
2. **Proteção contra Billion Laughs / Entity Expansion:** Entidades externas e expansões recursivas são desabilitadas no parser XML.
3. **Limite de Tamanho de Payload:** Arquivos com tamanho superior a 10 MB lançam `ArtifactTooLargeError`.

---

# 2. Garantia de Idempotência por SHA-256

- Cada XML submetido gera um hash `raw_xml_hash = SHA-256(bytes originais)`.
- A restrição `UNIQUE(raw_xml_hash)` e a chave primária `access_key` (44 dígitos) no PostgreSQL impedem duplicatas.
