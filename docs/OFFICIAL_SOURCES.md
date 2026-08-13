# LÉXORA — Especificação de Fontes Oficiais Brasileiras (Official Primary Sources)

Este documento estabelece o registro e as políticas de governança para as fontes oficiais primárias brasileiras integradas na **FASE 5** do **LÉXORA (LXR)**.

---

# 1. Famílias de Fontes Primárias Oficiais

| Família de Fonte | Entidade Institucional | Domínio Oficial Autorizado | Nível de Autoridade |
| :--- | :--- | :--- | :--- |
| **Presidência da República** | Secretaria-Geral / Subchefia para Assuntos Jurídicos | `planalto.gov.br`, `www.planalto.gov.br` | Level 5 (Máximo Nacional) |
| **Diário Oficial da União** | Imprensa Nacional / Presidência | `in.gov.br`, `dou.gov.br` | Level 5 (Publicação Oficial) |
| **Receita Federal do Brasil** | Ministério da Fazenda / RFB | `receita.fazenda.gov.br`, `rfb.gov.br` | Level 4 (Normas Tributárias) |
| **CONFAZ** | Conselho Nacional de Política Fazendária | `confaz.fazenda.gov.br` | Level 4 (Convênios ICMS) |

---

# 2. Princípio da Autoridade e Fontes Proibidas

- **Fontes Secundárias Proibidas:** Blogs, portais comerciais de notícias, fóruns, redes sociais ou consolidadores de terceiros **JAMAIS** possuem autoridade jurídica para a LÉXORA.
- **Hierarquia de Fontes:** Legislação e atos normativos somente são dados como verdadeiros se sua proveniência tiver origem rastreável em fonte primária de Nível 4 ou Nível 5.

---

# 3. Políticas de Rate Limiting e Polidez de Aquisição

- **Timeout Padrão:** 30 segundos.
- **Max Retries:** 3 tentativas com exponencial backoff (1s, 2s, 4s).
- **Rate Limit:** Máximo de 2 requisições por segundo por domínio.
- **Respeito a Bloqueios:** Se um servidor oficial retornar HTTP 429 (Too Many Requests) ou bloqueio, o agente registra a fonte como `UNAVAILABLE` e encerra a tentativa sem evasões.
