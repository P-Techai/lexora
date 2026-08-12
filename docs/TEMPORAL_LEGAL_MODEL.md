# LÉXORA — Especificação do Modelo Jurídico Temporal (Temporal Legal Model Specification)

Este documento descreve as 4 dimensões temporais, a matemática de intervalos semi-abertos, a detecção de conflitos/lacunas e o modelo de revogação imutável no **LÉXORA (LXR)**.

---

# 1. As 4 Dimensões Temporais

O LÉXORA distingue rigorosamente quatro dimensões temporais:

1. **`publication_date` (Data de Publicação):** Data em que a norma foi publicada no Diário Oficial.
2. **`effective_from` (Data de Início da Vigência):** Data em que a norma entra em vigor (considerando vacatio legis).
3. **`effective_until` (Data de Término da Vigência):** Data de revogação ou término de eficácia.
4. **`captured_at` (Data de Captura):** Timestamp técnico em que o artefato bruto foi coletado.

---

# 2. Matemática de Intervalos Semi-Abertos $[effective\_from, effective\_until)$

A vigência de uma `LegalVersion` segue o intervalo semi-aberto à direita:

$$\text{Vigente em } T \iff T \ge \text{effective\_from} \quad \land \quad (\text{effective\_until IS NULL} \lor T < \text{effective\_until})$$

### Exemplo de Transição Limite
- **Versão 1:** `effective_from = 2020-01-01`, `effective_until = 2024-07-01`
- **Versão 2:** `effective_from = 2024-07-01`, `effective_until = NULL`

- Em **2024-06-30**: Versão 1 ativa (`EFFECTIVE`).
- Em **2024-07-01**: Versão 1 expirada (`EXPIRED`), Versão 2 ativa (`EFFECTIVE`).

---

# 3. Auditoria de Conflitos e Lacunas (`TemporalIntegrityValidator`)

- **`TEMPORAL_CONFLICT` (Sobreposição / Overlap):** Detectado quando duas versões do mesmo documento declaram vigência para a mesma data $T$. O sistema registra o conflito e proíbe a escolha arbitrária por IA.
- **`TEMPORAL_GAP` (Lacuna):** Detectado quando há um intervalo sem cobertura normativa entre duas versões históricas.

---

# 4. Modelo de Revogação Total e Parcial (Imutabilidade Histórica)

- **REVOGAÇÃO NUNCA É DELETE SQL:** Nenhuma norma é excluída do banco de dados relacional.
- **Revogação Total (`RevokeLegalDocumentUseCase`):** Atualiza a versão ativa para `status = REVOKED`, encerra o `effective_until` na data da revogação e exige uma relação `REVOKES` vinculada à `Evidence`.
- **Revogação Parcial (`RevokeLegalNodeUseCase`):** Afeta individualmente um `LegalNode` específico (ex: Artigo 2º revogado), preservando intactos os demais artigos (Art. 1º e Art. 3º).
