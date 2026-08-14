# LÉXORA — Relatórios Executivos e Auditáveis (`FiscalExecutiveReport`)

Este documento especifica a geração de relatórios fiscais executivos e auditáveis no **LÉXORA (LXR)**.

---

# 1. Estrutura do Relatório Executivo

Todo relatório fiscal executivo contém:
1. Identificação do processamento e da empresa (`company_id`);
2. Data da operação (`operation_date`) e período de referência;
3. Fatos fiscais e produtos processados;
4. Resumo de tributos apurados (ICMS, ICMS-ST, IPI, PIS, COFINS, ISS, FCP, FCP-ST);
5. Memórias de cálculo `Decimal` com fórmulas explícitas;
6. Divergências identificadas (`FiscalDivergence`);
7. Itens com revisão humana pendente (`REVIEW_REQUIRED` / `CONFLICT`);
8. Rastreabilidade jurídica Two-Brain (evidências e nós normativos);
9. Versão do motor e assinatura imutável do relatório (`report_hash`).

---

# 2. Formatos de Exportação

- **JSON:** Exportação estruturada para integrações de API (`GET /api/v1/fiscal/decisions/{decision_id}/report`).
- **CSV:** Exportação tabular para auditoria e planilhas (`GET /api/v1/fiscal/decisions/{decision_id}/export`).
