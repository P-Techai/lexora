# Especificação de Domínio: Motor Fiscal e de Cálculo (Fiscal & Tax Calculation Engine Spec)

---

# 1. Motor Fiscal (Fiscal Rules Engine)

O motor fiscal realiza o enquadramento determinístico da operação tributária.

### Entradas (Inputs)
- **Dados do Emitente/Destinatário:** UF Origem, UF Destino, Regime Tributário (Simples Nacional, Lucro Presumido, Lucro Real), Tipo de Consumidor (Final / Revenda / Industrialização);
- **Dados do Produto:** NCM (8 dígitos), CEST (7 dígitos), Descrição do item;
- **Dados da Operação:** Data da operação, CFOP pretendido, Valor bruto, Frete, Seguro, Desconto, Outras despesas.

### Saídas (Outputs)
- **Classificação:** CST ou CSOSN aplicável; CFOP ajustado para a operação;
- **Alíquotas e Bases:** Alíquota nominal, Percentual de redução de base, Margem de Valor Agregado (MVA ST), Alíquota efetiva;
- **Fundamentação Legal:** Link para o dispositivo normativo cadastrado no `LegalNode` que autoriza o diferimento, isenção, redução ou alíquota aplicada.

---

# 2. Motor de Cálculo Determinístico (Calculation Engine)

- Implementação em código puro Python utilizando `Decimal` com arredondamento ABNT NBR 5891 / bancário (`ROUND_HALF_EVEN`).
- Impostos Suportados no Regime Atual: ICMS, ICMS-ST, DIFAL, IPI, PIS, COFINS, ISS.
- Impostos Suportados no Regime Dual da Reforma: CBS, IBS, IS.

### Schema do Registro Auditável de Memória de Cálculo (`TaxCalculationLog`)
```json
{
  "id": "uuid-v4",
  "operation_date": "2026-08-10",
  "company_regime": "LUCRO_REAL",
  "ncm": "84713012",
  "cfop": "5102",
  "cst": "000",
  "input_values": {
    "product_value": "1000.00",
    "freight": "50.00",
    "discount": "0.00"
  },
  "applied_formulas": {
    "icms_base": "product_value + freight - discount",
    "icms_value": "icms_base * (aliquot / 100)"
  },
  "calculated_taxes": {
    "icms": {
      "base": "1050.00",
      "aliquot": "18.00",
      "value": "189.00"
    }
  },
  "legal_grounds": [
    "RICMS-SP, Art. 52, Inciso I"
  ],
  "engine_version": "1.0.0",
  "calculation_hash": "sha256-hash-dos-inputs-e-resultados"
}
```
