# LÉXORA — Perfil Cadastral Fiscal do Produto (`FiscalProductProfile`)

Este documento especifica a representação de cadastro fiscal de produtos no **LÉXORA (LXR)** na **FASE 6.5**.

---

# 1. Atributos do Perfil

- `product_id`: ID único do produto.
- `sku`: Código interno de estoque.
- `gtin`: Código global GTIN/EAN de 13 dígitos.
- `description`: Descrição comercial original.
- `normalized_description`: Descrição em texto maiúsculo limpo.
- `ncm`: NCM validado de 8 dígitos numéricos.
- `cest`: CEST de 7 dígitos numéricos se aplicável.
- `unit`: Unidade comercial (ex: UN, KG, CX).
- `origin`: Origem da mercadoria (0 a 8).
- `fiscal_status`: Status (`CLASSIFIED`, `PARTIALLY_CLASSIFIED`, `REVIEW_REQUIRED`, `CONFLICT`, `UNCLASSIFIED`).
- `classification_confidence`: Métrica de confiança técnica (1.0 = certeza total).
- `classification_source`: Origem da classificação.
