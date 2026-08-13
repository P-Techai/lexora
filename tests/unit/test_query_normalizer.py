import pytest
from src.domain.services.query_normalizer import LegalQueryNormalizer


def test_query_normalizer_spaces_lowercase_and_accents():
    """Testa a normalização determinística de strings de consulta de busca."""
    raw_query = "  Artigo  1º ,  inciso I  da   LC  116/2003 "
    normalized = LegalQueryNormalizer.normalize_query(raw_query)

    assert "artigo 1º" in normalized
    assert "lc 116/2003" in normalized
    assert "  " not in normalized


def test_query_normalizer_identifier_extraction():
    """Testa a extração determinística de números de artigos e normas presentes na query."""
    query = "Prestação de serviços no Art. 1º da Lei 116"
    identifiers = LegalQueryNormalizer.extract_normative_identifiers(query)

    assert identifiers.get("article_number") in ("1º", "1")
    assert identifiers.get("document_number") == "116"
