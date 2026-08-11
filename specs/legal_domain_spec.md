# Especificação de Domínio: Conhecimento Jurídico (Legal Knowledge Domain)

---

# 1. Modelo de Dados de Dispositivo Normativo (`LegalNode`)

A legislação brasileira é representada como uma árvore hierárquica rigorosamente preservada, evitando estilhaçamento arbitrário (chunking cego).

### Hierarquia de Tipos de Dispositivo (`LegalNodeType`)
- `NORMA` (Constituição, LC, LO, Decreto, IN, Resolução)
- `LIVRO`
- `TITULO`
- `CAPITULO`
- `SECAO`
- `SUBSECAO`
- `ARTIGO`
- `PARAGRAFO`
- `INCISO`
- `ALINEA`
- `ITEM`
- `NOTA`

### Campos Obrigatórios do `LegalNode`
```json
{
  "id": "uuid-v4",
  "norma_id": "uuid-norma",
  "node_type": "ARTIGO",
  "number": "Art. 3º",
  "text": "Texto oficial e integral do artigo...",
  "parent_id": "uuid-parent-secao",
  "path": "/norma-123/livro-1/titulo-2/capitulo-1/artigo-3",
  "position": 14,
  "metadata": {
    "jurisdiction": "FEDERAL",
    "issuing_body": "PRESIDENCIA_DA_REPUBLICA",
    "official_source_url": "https://www.planalto.gov.br/...",
    "official_gazette_date": "1996-09-16"
  },
  "effective_from": "1996-09-16",
  "effective_until": null,
  "version": 1,
  "status": "ACTIVE",
  "content_hash": "sha256-hash-do-texto"
}
```

---

# 2. Relações Normativas (`LegalRelation`)

O grafo jurídico mapeia conexões explícitas entre dispositivos normativos:

- `AMENDS`: Altera a redação de dispositivo anterior.
- `REVOKES`: Revoga (expressa ou tacitamente) dispositivo anterior.
- `REGULATES`: Regulamenta norma de hierarquia superior.
- `REFERENCES`: Cita outro dispositivo legal.
- `COMPLEMENTS`: Inserção de regra complementar.
- `SUPERSEDES`: Substitui norma anterior em matéria específica.
- `RATIFIES`: Ratifica decreto ou tratado.
- `SUSPENDS`: Suspende a eficácia de dispositivo por decisão judicial/legislativa.

---

# 3. Resolução de Conflito e Hierarquia

O raciocínio de precedência jurídica segue a matriz ponderada:
1. **Competência Constitucional:** Competência legislativa da União vs. Estado vs. Município.
2. **Hierarquia:** Norma Constitucional > Lei Complementar > Lei Ordinária > Decreto > Instrução Normativa.
3. **Especialidade:** Norma especial prevalece sobre norma geral em seu âmbito de aplicação (`Lex specialis derogat legi generali`).
4. **Temporalidade:** Norma posterior revoga norma anterior no que for incompatível (`Lex posterior derogat legi priori`).
5. **Vigência:** Verificação estrita se a norma estava em vigor na data da operação fiscal (`effective_from <= date_of_operation <= effective_until`).
