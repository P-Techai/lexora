import pytest
from src.application.parsers.brazilian_law_parser import BrazilianLawParser
from src.domain.enums import ChangeStatus


def test_tree_parsing_multi_process_reproducibility():
    """
    TESTE DE REPRODUTIBILIDADE MULTI-PROCESSO:
    Processa o mesmo texto normativo em duas instâncias independentes.
    Garante que a identidade lógica (logical_id), caminhos (path), tipos e content_hash
    são 100% idênticos sem dependência de UUIDs gerados aleatoriamente.
    """
    raw_text = """LEI ORDINÁRIA Nº 10.406, DE 10 DE JANEIRO DE 2002
PARTE GERAL
LIVRO I
DOS BENS
TÍTULO ÚNICO
DAS DIFERENTES CLASSES DE BENS
Art. 79. São bens imóveis o solo e tudo quanto se lhe incorporar natural ou artificialmente."""

    parser_A = BrazilianLawParser()
    parser_B = BrazilianLawParser()

    nodes_A, warnings_A = parser_A.parse_structure(raw_text, version_id="ver-cc2002")
    nodes_B, warnings_B = parser_B.parse_structure(raw_text, version_id="ver-cc2002")

    assert len(nodes_A) == len(nodes_B)

    for nA, nB in zip(nodes_A, nodes_B):
        assert nA.logical_id == nB.logical_id, f"Identidade lógica divergente: {nA.logical_id} != {nB.logical_id}"
        assert nA.path == nB.path, f"Path divergente: {nA.path} != {nB.path}"
        assert nA.node_type == nB.node_type, f"Tipo divergente: {nA.node_type} != {nB.node_type}"
        assert nA.content_hash == nB.content_hash, f"Hash canônico divergente: {nA.content_hash} != {nB.content_hash}"
        assert nA.identifier == nB.identifier


def test_reingestion_change_status_enum_contract():
    """Testa que os status de mudança são rigorosamente NEW, UNCHANGED e CHANGED (sem UPDATED legado)."""
    assert ChangeStatus.NEW == "NEW"
    assert ChangeStatus.UNCHANGED == "UNCHANGED"
    assert ChangeStatus.CHANGED == "CHANGED"
    assert ChangeStatus.REMOVED == "REMOVED"
    assert ChangeStatus.UNAVAILABLE == "UNAVAILABLE"
