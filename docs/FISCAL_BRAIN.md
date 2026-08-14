# LÉXORA — Especificação do Cérebro Fiscal (Fiscal Brain)

Este documento especifica a arquitetura e componentes do **Fiscal Brain** do **LÉXORA (LXR)** implementados na **FASE 6.3**.

---

# 1. Visão Geral

O **Fiscal Brain** é o subsistema responsável pela aplicação determinística de regras tributárias brasileiras formalizadas sobre fatos fiscais observados.

### Princípios Fundamentais:
- **Zero LLM em Decisões Tributárias:** Alíquotas, bases de cálculo, reduções, isenções, CST, CFOP e NCM são calculados e classificados por código determinístico.
- **Cálculo Decimal Estrito:** Todo cálculo financeiro/tributário utiliza a classe `Decimal` do Python com a política `TaxRoundingService` (`ROUND_HALF_UP`).
- **Validação Temporal contra Data da Operação:** Regras tributárias são avaliadas contra `fact.operation_date`, NUNCA contra a data atual do servidor.
- **Conexão com a Verdade Normativa:** Toda regra fiscal em status `ACTIVE` deve estar obrigatoriamente vinculada a um nó normativo legal, versão e evidência do **Legal Brain**.

---

# 2. Entidades Principais

- `FiscalFact`: Fatos fiscais observados da operação (empresa, regime, UF, data, produto, valores, NCM, CST, CFOP).
- `FiscalProductProfile`: Perfil de produto com status de classificação explícito (`CONFIRMED`, `PROVISIONAL`, `REVIEW_REQUIRED`, `UNKNOWN`).
- `FiscalTaxRule`: Regra fiscal formalizada contendo alíquota, fórmula, jurisdição, vigência temporal e vínculo com o Legal Brain.
- `TaxCalculation`: Resultado do cálculo individual por imposto (ICMS, ICMS_ST, IPI, PIS, COFINS, ISS, CBS, IBS, IS).
- `TaxCalculationLog`: Memória de cálculo auditável e imutável gravada no PostgreSQL com `ON DELETE RESTRICT`.

---

# 3. Tributos Suportados

1. **ICMS & ICMS_ST:** Operações internas, interestaduais, importação, com redução de base e isenções.
2. **IPI:** Alíquotas de TIPI com validação de NCM.
3. **PIS / COFINS:** Regime cumulativo e não-cumulativo.
4. **ISS:** Regras municipais por código de serviço.
5. **Reforma Tributária (CBS, IBS, IS):** Motores estruturais preparados para a nova legislação tributária brasileira.
