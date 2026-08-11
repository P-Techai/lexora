# Regra de Agente: 03 — Determinismo e Memória de Cálculo Tributária (Calculation Determinism Rule)

---

# 1. Proibição de Uso de LLM para Cálculos Financeiros

> [!WARNING]
> **NUNCA UTILIZE LLMS PARA EXECUTAR CÁLCULOS TRIBUTÁRIOS OU FINANCEIROS CRÍTICOS.**

- Modelos de Linguagem são probabilísticos e inaptos para operações aritméticas que exigem precisão contábil e fiscal legalmente vinculante.
- Todos os cálculos de impostos (ICMS, PIS, COFINS, ISS, IPI, CBS, IBS, IS) devem ser executados por **código determinístico puro em Python** utilizando o tipo `Decimal` para evitar imprecisões de ponto flutuante.

---

# 2. Requisito de Memória Auditável de Cálculo

Todo processamento de cálculo tributário deve gerar um registro imutável de memória de cálculo (`TaxMemoryLog`) contendo:

1. **Inputs:** Todos os parâmetros de entrada (valor da operação, NCM, CEST, UF origem/destino, regime tributário, tipo de cliente);
2. **Fórmula:** Identificação clara da equação matemática utilizada;
3. **Versão da Regra:** Hash ou ID da versão da regra fiscal em vigor na data da operação;
4. **Resultado:** Valores calculados de base, alíquota, reduções, benefícios e imposto devido;
5. **Fundamento Legal:** Citação explícita dos artigos normativos que fundamentam a alíquota e o benefício aplicados;
6. **Engine Version & Timestamp:** Versão do motor de cálculo e data/hora do processamento.
