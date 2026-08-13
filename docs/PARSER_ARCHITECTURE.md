# LÉXORA — Arquitetura de Parsers Estruturais de Legislação Brasileira

Este documento especifica a arquitetura extensível de parsers estruturais do **LÉXORA (LXR)** para decomposição determinística de normas jurídicas brasileiras.

---

# 1. Hierarquia de Nós Normativos Reconhecidos

O parser estrutural brasileiro reconhece e categoriza deterministicamente os seguintes tipos de nós normativos (`LegalNodeType`):

- **`NORMA`**: Nó raiz estrutural determinístico representando o ato normativo como um todo (substitui qualquer dependência informal de `nodes[0]`).
- **`LIVRO`**, **`TÍTULO`**, **`CAPÍTULO`**, **`SEÇÃO`**, **`SUBSEÇÃO`**: Blocos estruturais de agrupamento.
- **`ARTIGO`**: Unidade fundamental do texto normativo (ex.: `Art. 1º`, `Art. 2º`).
- **`PARAGRAFO`**: Desdobramentos do artigo (ex.: `§ 1º`, `§ 2º`, `Parágrafo único.`).
- **`INCISO`**: Enumeração vinculada a artigo ou parágrafo (ex.: `I -`, `II -`).
- **`ALINEA`**: Sub-enumeração alfabética (ex.: `a)`, `b)`).
- **`ITEM`**: Sub-enumeração numérica de alínea (ex.: `1.`, `2.`).
- **`ANEXO`**: Anexo estruturado ou tabela normativa.
- **`NOTA`**: Texto não classificado explicitamente preservado para garantir **Zero Silent Data Loss**.

---

# 2. Padrões de Numeração e Expressões Regulares Reconhecidas

- **Artigos:** `^Art\.\s*(\d+[ºo°]?|\d+)\.?`
- **Parágrafos:** `^§\s*(\d+[ºo°]?|\d+)\.?` ou `^Parágrafo\s+único\.?`
- **Incisos:** `^([MCDXLVIICLDVIX]+)\s*[-–—]?`
- **Alíneas:** `^([a-z])\)`
- **Itens:** `^(\d+)\.`

---

# 3. Preservação Estrita de Texto

- **`text` (RAW TEXT):** Armazena o texto exato do dispositivo sem alterar ortografia, pontuação ou formatação original.
- **`normalized_text` (NORMALIZED TEXT):** Unicode NFKC, caixa baixa, espaços unificados para fins de comparação e busca.
- **Nenhum uso de LLM:** O parser funciona 100% via regras gramaticais e de máquina de estados determinística.
