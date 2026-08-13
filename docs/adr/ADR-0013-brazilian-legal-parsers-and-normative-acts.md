# ADR-0013: Arquitetura de Parsers de Legislação Brasileira, Camada de Extração e Nó Raiz NORMA

## Context
Na Fase 5 do LÉXORA, iniciou-se a ingestão oficial controlada de legislação brasileira real. Identificou-se a necessidade de desacoplar a decodificação de formatos (HTML/PDF/TXT) da decomposição gramatical estrutural de normas, reconhecer a hierarquia brasileira (`NORMA` a `ITEM`) e proibir o uso informal de `nodes[0]` como raiz jurídica.

## Decision
1. **Separação entre Extração e Parsing:** Criada a porta `DocumentExtractor` para decodificar HTML/TXT/PDF em texto bruto. A porta `LegalStructureParser` recebe texto bruto e constrói a árvore de `LegalNode` sem conhecimento de formatos de arquivos ou HTTP.
2. **Reconhecimento da Hierarquia Brasileira:** Criado o `BrazilianLawParser` (versão `brazilian-law-parser@1.0.0`) reconhecendo `NORMA`, `LIVRO`, `TÍTULO`, `CAPÍTULO`, `SEÇÃO`, `SUBSEÇÃO`, `ARTIGO`, `PARÁGRAFO`, `INCISO`, `ALÍNEA`, `ITEM`, `ANEXO`.
3. **Nó Raiz Determinístico `NORMA`:** Estabelecido o nó com `node_type = LegalNodeType.NORMA` e `parent_id = None` como a raiz estrutural e jurídica de cada versão. Proibida qualquer dependência incidental de `nodes[0]`.
4. **Preservação Estrita de Texto (Zero Silent Data Loss):** Armazenamento de `raw_text` (intacto) e `normalized_text` (NFKC/caixa baixa) separadamente. Linhas não classificadas tornam-se nós `NOTA` com warning.
5. **Declaração de Infraestrutura:** Integração com Neon PostgreSQL estabelecida via `DATABASE_URL`. Supabase e Cloudflare permanecem não integrados.

## Consequences
- Garantia de 100% de integridade estrutural e reprodutibilidade gramatical no parsing de legislação brasileira real.
