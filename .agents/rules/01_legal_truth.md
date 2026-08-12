# Regra de Agente: 01 — Princípio da Verdade Jurídica Temporal

---

# 1. Verdade Jurídica

A Verdade Jurídica no **LÉXORA (LXR)** é intrinsecamente **TEMPORAL** e reside estritamente em dispositivos normativos (`LegalNode`) e versões históricas (`LegalVersion`) fundadas em fontes primárias.

---

# 2. Princípios Invioláveis de Tempo e Vigência

1. **TEMPO É PARTE DA VERDADE JURÍDICA:** O sistema jamais deve responder a uma consulta jurídica ou tributária sem considerar o momento no tempo (data de referência $T$).
2. **Proibição de `datetime.now()` Implícito:** A data jurídica deve ser sempre explicitada pela aplicação ou pelo caso de uso.
3. **Quatro Dimensões Temporais:** Distinguir sempre `publication_date`, `effective_from`, `effective_until` e `captured_at`.
4. **Semântica do Intervalo Semi-Aberto:** Os períodos de vigência adotam a matemática $[effective\_from, effective\_until)$.
5. **Imutabilidade Histórica & Revogação por Evento:** Revogar uma norma é um evento jurídico que altera a vigência e registra a relação com a evidência responsável. **É EXPRESSAMENTE PROIBIDO EXECUTAR DELETE SQL EM DADOS HISTÓRICOS DE LEGISLAÇÃO.**
6. **Não-Resolução Silenciosa de Conflitos:** Qualquer sobreposição de vigências (`OVERLAP`) deve produzir o estado `TEMPORAL_CONFLICT`. É proibido usar LLMs ou heurísticas silenciosas para decidir qual norma vigora.
