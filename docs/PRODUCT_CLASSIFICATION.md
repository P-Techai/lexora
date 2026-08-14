# LÉXORA — Classificação Fiscal de Produtos (`ProductClassification`)

Este documento especifica os estados determinísticos de classificação fiscal de produtos no **LÉXORA (LXR)** na **FASE 8**.

---

# 1. Estados Determinísticos de Classificação

O `ProductFiscalClassificationService` retorna exclusivamente os seguintes estados formais:
- `DETERMINED`: NCM, CEST e regras totalmente validadas.
- `AMBIGUOUS`: Múltiplas classificações plausíveis (encaminhado para revisão).
- `INSUFFICIENT_DATA`: Dados cadastrais incompletos.
- `CONFLICT`: Conflito entre padrões cadastrais.
- `INVALID`: NCM com formato estrutural incorreto (diferente de 8 dígitos numéricos).
- `REQUIRES_HUMAN_REVIEW`: Obriga intervenção humana sem estimativa probabilística de I.A.
