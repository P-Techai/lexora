# LÉXORA — Catálogo Versionado de Regras Fiscais (`FiscalRuleCatalog`)

Este documento especifica a estrutura do catálogo oficial de regras fiscais do **LÉXORA (LXR)** na **FASE 8**.

---

# 1. Estrutura do Item do Catálogo

Cada regra tributária oficial cadastrada no sistema possui:
- `rule_id`: Identificador único da regra.
- `version`: Versão da regra (ex: `1.0`).
- `valid_from` & `valid_until`: Janela temporal de vigência jurídica.
- `jurisdiction`: Jurisdição (`FEDERAL`, `STATE`, `MUNICIPAL`).
- `tax_type`: Tributo (`ICMS`, `ICMS_ST`, `DIFAL`, `FCP`, `IPI`, `PIS`, `COFINS`, `ISS`).
- `state` / `municipality`: UF ou município de competência.
- `rate`: Alíquota em precisão `Decimal`.
- `base_reduction` & `mva_rate`: Redução de base e Margem de Valor Agregado.
- `evidence`: Vínculo à evidência jurídica oficial (`source_org`, `legal_act`, `article`, `url`, `acquisition_date`).
- `content_hash`: Hash SHA-256 garantindo imutabilidade do catálogo.
