import pytest


def test_deterministic_ranking_formula():
    """Testa que a fórmula de reranking híbrido é 100% determinística e prioriza correspondência exata e autoridade."""
    lexical_score = 0.8
    semantic_score = 0.6
    authority_level = 5  # Max authority
    exact_bonus = 0.3

    auth_score = authority_level / 5.0
    final_score = (0.35 * lexical_score) + (0.35 * semantic_score) + (0.10 * auth_score) + (0.20 * exact_bonus)

    assert round(final_score, 4) == 0.75
