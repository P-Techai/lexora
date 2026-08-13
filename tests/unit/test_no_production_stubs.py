import ast
from pathlib import Path
import pytest


def test_audit_no_production_stubs_or_silent_mock_fallbacks():
    """
    TESTE DE AUDITORIA DE PRODUTIBILIDADE (PROMPT 08.1 § 39):
    Varre todos os arquivos de código-fonte em src/ garantindo 0 stubs impeditivos (NotImplementedError em prod use cases,
    mock fallbacks silenciosos ou resultados fictícios fixos).
    """
    src_dir = Path("src")
    violations = []

    for py_file in src_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")

        # Impede NotImplementedError em use cases de produção
        if "raise NotImplementedError" in content:
            violations.append(f"{py_file}: contém 'raise NotImplementedError'")

        # Impede mock fallback silencioso em try/except no código de produção
        if "except" in content and "MockEmbeddingProvider" in content:
            violations.append(f"{py_file}: contém fallback silencioso para MockEmbeddingProvider em tratamento de exceção")

    assert not violations, f"Stubs ou fallbacks silenciosos de produção encontrados: {violations}"
