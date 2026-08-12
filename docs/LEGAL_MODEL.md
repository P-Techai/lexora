# LÉXORA — Modelo Jurídico Canônico (Canonical Legal Model)

Este documento especifica o **Modelo Jurídico Canônico** do **LÉXORA (LXR)**.

---

# 1. Princípio do Conhecimento Estruturado

> [!CRITICAL]
> **O CONHECIMENTO JURÍDICO ESTRUTURADO É A FONTE ÚNICA DA VERDADE.**
> O banco de dados normativo não é um mero repositório de textos cortados (chunks arbitrários) com embeddings. O vetor (embedding) é uma representação derivada. O conhecimento normativo canônico é preservado em 6 camadas estritas de provenance:
> `SOURCE` → `LEGAL DOCUMENT` → `LEGAL VERSION` → `LEGAL NODE` (Árvore) → `LEGAL RELATION` → `EVIDENCE`.

```
           +--------------------+
           |       SOURCE       | (Origem Oficial: Planalto, Receita, CONFAZ)
           +---------+----------+
                     |
           +---------v----------+
           |   LEGAL DOCUMENT   | (Lei nº 8.112/1990, Constituição, Decreto X)
           +---------+----------+
                     |
           +---------v----------+
           |    LEGAL VERSION   | (Versão Histórica com Vigência Temporal)
           +---------+----------+
                     |
           +---------v----------+
           |     LEGAL NODE     | (Hierarquia: Artigo -> Parágrafo -> Inciso)
           +----+----------+----+
                |          |
      +---------v--+    +--v-----------------+
      |  EVIDENCE  |    |   LEGAL RELATION   | (AMENDS, REVOKES, REGULATES)
      +------------+    +--------------------+
```

---

# 2. Entidades Canônicas

### 1. `Source` (Origem)
- **Papel:** Representa o órgão gestor ou portal emissor da norma.
- **Campos:** `id`, `name`, `official`, `authority_level` (1 a 5), `base_url`, `jurisdiction`, `active`.
- **Diferenciação:** `authority_level` representa a confiabilidade da fonte (ex.: 1 para Planalto/DOU, 4 para blogs comunitários). Não se confunde com a hierarquia da norma.

### 2. `LegalDocument` (Unidade Documental)
- **Papel:** Identidade única de um ato normativo.
- **Campos:** `id`, `source_id`, `document_type`, `document_number`, `title`, `ementa`, `jurisdiction`, `issuing_body`, `publication_date`, `official_url`, `document_hash`.
- **Unicidade:** O número isolado (`document_number`) não é único. A unicidade exige a combinação com `source_id`, `document_type` e `jurisdiction`.

### 3. `LegalVersion` (Versão Histórica)
- **Papel:** Preserva a alteração histórica sem jamais sobrescrever textos antigos.
- **Campos:** `id`, `legal_document_id`, `version_number`, `content_hash`, `published_at`, `effective_from`, `effective_until`, `status`, `source_document_url`, `raw_storage_key`, `parser_version`.
- **Consulta de Vigência:** Método `is_effective_on(target_date)` responde se a versão estava vigente na data da operação fiscal consultada.

### 4. `LegalNode` (Dispositivo Estrutural)
- **Papel:** Nó em árvore com auto-referência (`parent_id`), posição ordinal (`position`) e caminho (`path`).
- **Tipos de Nó:** `NORMA`, `LIVRO`, `TITULO`, `CAPITULO`, `SECAO`, `SUBSECAO`, `ARTIGO`, `PARAGRAFO`, `INCISO`, `ALINEA`, `ITEM`, `NOTA`, `ANEXO`, `OUTRO`.
- **Reconstrução Determinística:** O campo `position` garante a ordem exata dos incisos e parágrafos dentro de um artigo.

### 5. `LegalRelation` (Aresta de Grafo Normativo)
- **Papel:** Relação semântico-normativa entre dispositivos.
- **Tipos:** `AMENDS`, `REVOKES`, `REGULATES`, `REFERENCES`, `COMPLEMENTS`, `SUPERSEDES`, `RATIFIES`, `VETOES`, `SUSPENDS`.
- **Campos:** `id`, `source_node_id`, `target_node_id`, `relation_type`, `effective_from`, `effective_until`, `confidence`, `evidence_id`.

### 6. `Evidence` (Evidência Documental)
- **Papel:** Registra o trecho bruto oficial que comprova uma afirmação ou relação.
- **Campos:** `id`, `source_id`, `legal_document_id`, `legal_version_id`, `legal_node_id`, `source_url`, `quote_or_excerpt`, `locator`, `content_hash`, `captured_at`.
