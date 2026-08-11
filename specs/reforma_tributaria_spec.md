# Especificação de Domínio: Módulo da Reforma Tributária (Tax Reform Module Spec)

---

# 1. Dualidade do Sistema Tributário Brasileiro

A Reforma Tributária (Emenda Constitucional nº 132/2023) introduz a transição gradual do sistema atual para o modelo de Imposto sobre Valor Agregado (IVA) Dual:

| Regime Atual | Novo Regime (Reforma Tributária) | Competência |
| :--- | :--- | :--- |
| **PIS / COFINS** | **CBS** (Contribuição sobre Bens e Serviços) | Federal |
| **ICMS / ISS** | **IBS** (Imposto sobre Bens e Serviços) | Estadual / Municipal (Comitê Gestor) |
| **IPI** | **IS** (Imposto Seletivo) | Federal |

---

# 2. Motor de Simulação de Cenários

O LÉXORA permite comparar visualmente e numericamente três perguntas fundamentais para planejamento fiscal:

1. **"Como é hoje?"** (Cálculo com PIS, COFINS, ICMS, ISS e IPI).
2. **"Como será na data X?"** (Cálculo respeitando o cronograma oficial de transição e alíquotas de teste/efetivas).
3. **"Qual o impacto e variação financeira?"** (Comparativo percentual de carga tributária e aproveitamento de créditos).

---

# 3. Cronograma e Vigência Temporal

O motor tributário utilizará a data da operação para aplicar automaticamente as regras da fase de transição:

- **2026:** Alíquotas de teste de CBS (0,9%) e IBS (0,1%);
- **2027:** Extinção de PIS/COFINS, cobrança integral da CBS e introdução do Imposto Seletivo (IS);
- **2029 a 2032:** Transição gradual com redução proporcional de ICMS/ISS e elevação proporcional do IBS;
- **2033:** Extinção completa de ICMS e ISS, vigência plena do modelo IBS/CBS/IS.
