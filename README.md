# LÉXORA — Plataforma Inteligente de Conhecimento Jurídico, Tributário e Contábil

[![Status](https://img.shields.io/badge/Status-Phase_6.2_Sealed_v0.9.1-blue.svg)](docs/CURRENT_STATE.md)
[![Architecture](https://img.shields.io/badge/Architecture-Clean_Architecture_4_Layers-green.svg)](docs/ARCHITECTURE.md)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

**Nome Oficial:** LÉXORA  
**Sigla:** LXR  
**Nome Técnico:** `lexora`

---

## 📌 Visão Geral

O **LÉXORA** é uma plataforma inteligente modular projetada para o ecossistema jurídico e fiscal brasileiro. Desenvolvido sob princípios rigorosos de **Clean Architecture**, o sistema garante:

1. **Verdade Jurídica Rastreável:** Respostas fundamentadas estritamente em fontes primárias oficiais e dispositivos normativos canônicos versionados.
2. **Determinismo Fiscal:** Cálculos tributários (ICMS, PIS, COFINS, ISS, IPI, CBS, IBS, IS) executados por código determinístico puro com memória auditável (`TaxCalculationLog`).
3. **Portabilidade sem Lock-in:** Arquitetura desacoplada baseada em *Ports & Adapters*, operando inicialmente em infraestrutura gratuita (Supabase, Cloudflare R2, Neon) com suporte total a migração para infraestrutura proprietária ou on-premises.

---

## 🚀 Como Iniciar

### 1. Iniciar o ambiente Docker local
```bash
cd infrastructure
docker-compose up -d
```

### 2. Configurar o ambiente Python
```bash
python -m venv .venv
source .venv/bin/activate  # ou .venv\Scripts\activate no Windows
pip install -r requirements.txt
```

### 3. Executar os Testes Unitários
```bash
pytest
```

---

## 📚 Documentação do Repositório

Toda a inteligência e memória arquitetural do projeto são mantidas em:

- 📖 [docs/PROJECT.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/PROJECT.md) — Visão geral e princípio da verdade jurídica
- 🏛️ [docs/ARCHITECTURE.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/ARCHITECTURE.md) — Detalhamento da Clean Architecture e Diagramas
- 🗺️ [docs/ROADMAP.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/ROADMAP.md) — Marcos de desenvolvimento (Fases 1 a 6)
- 📍 [docs/CURRENT_STATE.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/CURRENT_STATE.md) — Estado atual do repositório
- 🤝 [docs/HANDOFF.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/HANDOFF.md) — Guia de onboarding para novos agentes e desenvolvedores
- 📋 [docs/DECISIONS.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/DECISIONS.md) — Registros de Decisões Arquiteturais (ADRs)
- 📜 [docs/CHANGELOG.md](file:///c:/Users/Pedro/OneDrive/Desktop/lexora/docs/CHANGELOG.md) — Histórico de versões
