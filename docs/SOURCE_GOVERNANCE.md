# LÉXORA — Especificação de Governança de Fontes (Source Governance Specification)

Este documento especifica o **Source Registry** e os mecanismos de segurança e política de acesso a fontes normativas no **LÉXORA (LXR)**.

---

# 1. Registro e Políticas de Fonte (`SourcePolicy`)

Cada fonte cadastrada no sistema é associada a uma política estrita:

- `PRIMARY_OFFICIAL`: Portais oficiais primários da União (Diário Oficial da União, Planalto, Receita Federal, STF, STJ, CARF, CONFAZ).
- `SECONDARY_OFFICIAL`: Secretarias estaduais e municipais de Fazenda.
- `OFFICIAL_MIRROR`: Espelhos oficiais autorizados de atos normativos.
- `REFERENCE`: Portais técnicos de referência jurídica.
- `UNTRUSTED`: Fontes não autorizadas (bloqueadas automaticamente).

---

# 2. Allowlist de Domínios e Proteção SSRF (`URLSecurityValidator`)

O componente `URLSecurityValidator` garante que a aplicação jamais execute requisições HTTP arbitrárias:

- **Dominio Autorizado:** Toda URL consultada deve pertencer explicitamente à lista `allowed_domains` da fonte.
- **Bloqueio SSRF Estrito:** Requisições direcionadas para `localhost`, `127.0.0.1`, `0.0.0.0`, redes privadas (`10.x`, `172.16-31.x`, `192.168.x`), endpoints de metadados de nuvem (`169.254.169.254`) e esquemas não-HTTP/HTTPS disparam `SSRFProtectionError`.
