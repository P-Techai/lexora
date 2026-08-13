# LÉXORA — Especificação de Guardrails de Resposta Jurídica (Legal Answer Guardrails)

Este documento especifica a suíte de guardrails determinísticos que validam e autorizam a entrega de respostas jurídicas no **LÉXORA (LXR)**.

---

# 1. Matriz de Guardrails Centrais

| Guardrail | Responsabilidade | Ação em Caso de Violação |
| :--- | :--- | :--- |
| **`CitationValidator`** | Garante que toda afirmação e citação pertença a um `LegalNode` existente no contexto. | Rejeita a resposta e aciona `AbstentionPolicy` (`INSUFFICIENT_EVIDENCE`). |
| **`TemporalAnswerGuard`** | Confirma que os dispositivos citados estavam vigentes na `reference_date` solicitada. | Rejeita a resposta e aciona `AbstentionPolicy` (`TEMPORAL_CONFLICT`). |
| **`ProvenanceGuard`** | Valida a presença dos 5 elos de proveniência (`Node -> Version -> Evidence -> Artifact -> Source`). | Rejeita a resposta e aciona `AbstentionPolicy` (`PROVENANCE_FAILURE`). |
| **`ConflictGuard`** | Detecta ambiguidade estrutural ou coexistência de versões conflitantes no mesmo contexto. | Rejeita a resposta e aciona `AbstentionPolicy` (`CONFLICTING_SOURCES`). |
| **Prompt Injection Defense** | Trata o conteúdo dos documentos como DADOS puros em blocos isolados. | Impede a execução de instruções contidas em textos normativos. |

---

# 2. Respostas Estruturadas de Abstenção

O sistema nunca alucina ou preenche lacunas com conhecimentos externos. Em caso de insuficiência de dados ou falha de guardrail, é gerado o DTO `LegalAnswer` com `abstained = true` e o status apropriado.
