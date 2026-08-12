from datetime import datetime
import pytest

from src.domain.entities.legal_node import LegalNode
from src.domain.enums import LegalNodeType
from src.domain.exceptions import (
    InconsistentPositionError,
    InvalidLegalNodeError,
    TreeCycleDetectedError,
)
from src.domain.services.hash_service import DocumentHashCalculator
from src.domain.services.normalization_service import LegalNormalizationService
from src.domain.services.path_builder import LegalNodePathBuilder
from src.domain.services.tree_validator import LegalTreeIntegrityValidator
from src.application.ports.structure_parser import SyntheticLegalStructureParser


def test_hash_calculator_deterministic():
    text1 = "Art. 1º Esta Lei institui o Regime Jurídico dos Servidores..."
    text2 = "Art. 1º Esta Lei institui o Regime Jurídico dos Servidores..."
    text3 = "Art. 1º Outro texto..."

    hash1 = DocumentHashCalculator.calculate_sha256(text1)
    hash2 = DocumentHashCalculator.calculate_sha256(text2)
    hash3 = DocumentHashCalculator.calculate_sha256(text3)

    assert len(hash1) == 64
    assert hash1 == hash2
    assert hash1 != hash3


def test_normalization_service_clean_whitespace_and_unicode():
    raw_text = "Art. 1º  Esta Lei \r\n institui o   Regime Jurídico.\n\n"
    normalized = LegalNormalizationService.normalize_text(raw_text)

    assert "Art. 1º Esta Lei" in normalized
    assert "institui o Regime Jurídico." in normalized
    assert "\r" not in normalized


def test_path_builder_deterministic():
    path_root = LegalNodePathBuilder.build_path("art-1", parent=None)
    assert path_root == "/art-1"

    dummy_parent = LegalNode(
        id="parent-1",
        legal_version_id="ver-1",
        node_type=LegalNodeType.ARTIGO,
        identifier="art-1",
        label="Art. 1º",
        text="Text",
        path="/art-1",
        position=1,
        content_hash="h1"
    )

    path_child = LegalNodePathBuilder.build_path("par-1", parent=dummy_parent)
    assert path_child == "/art-1/par-1"


def test_tree_integrity_validator_cycle_detection():
    # Cria ciclo artificial: node-1 -> node-2 -> node-1
    node1 = LegalNode(
        id="node-1",
        legal_version_id="ver-1",
        parent_id="node-2",
        node_type=LegalNodeType.ARTIGO,
        identifier="art-1",
        label="Art. 1º",
        text="Text",
        path="/art-1",
        position=1,
        content_hash="h1"
    )

    node2 = LegalNode(
        id="node-2",
        legal_version_id="ver-1",
        parent_id="node-1",
        node_type=LegalNodeType.PARAGRAFO,
        identifier="par-1",
        label="§ 1º",
        text="Text",
        path="/art-1/par-1",
        position=1,
        content_hash="h2"
    )

    with pytest.raises(TreeCycleDetectedError):
        LegalTreeIntegrityValidator.validate_tree([node1, node2], expected_version_id="ver-1")


def test_tree_integrity_validator_duplicate_position_rejection():
    # Nós no mesmo nível com a mesma posição ordinal (position=1)
    node1 = LegalNode(
        id="node-1",
        legal_version_id="ver-1",
        parent_id="root",
        node_type=LegalNodeType.PARAGRAFO,
        identifier="par-1",
        label="§ 1º",
        text="Text",
        path="/art-1/par-1",
        position=1,
        content_hash="h1"
    )

    node2 = LegalNode(
        id="node-2",
        legal_version_id="ver-1",
        parent_id="root",
        node_type=LegalNodeType.PARAGRAFO,
        identifier="par-2",
        label="§ 2º",
        text="Text",
        path="/art-1/par-2",
        position=1,  # DUPLICADA!
        content_hash="h2"
    )

    root = LegalNode(
        id="root",
        legal_version_id="ver-1",
        parent_id=None,
        node_type=LegalNodeType.ARTIGO,
        identifier="art-1",
        label="Art. 1º",
        text="Text",
        path="/art-1",
        position=1,
        content_hash="h0"
    )

    with pytest.raises(InconsistentPositionError):
        LegalTreeIntegrityValidator.validate_tree([root, node1, node2], expected_version_id="ver-1")


def test_synthetic_structure_parser():
    raw = """
    Art. 1º Esta é uma lei sintética de teste.
    § 1º O primeiro parágrafo.
    I - O primeiro inciso.
    a) A primeira alínea.
    """

    parser = SyntheticLegalStructureParser()
    nodes = parser.parse_structure(raw, legal_version_id="ver-synthetic-1")

    assert len(nodes) == 4
    assert nodes[0].node_type == LegalNodeType.ARTIGO
    assert nodes[1].node_type == LegalNodeType.PARAGRAFO
    assert nodes[2].node_type == LegalNodeType.INCISO
    assert nodes[3].node_type == LegalNodeType.ALINEA

    # Verifica integridade da árvore gerada pelo parser sintético
    LegalTreeIntegrityValidator.validate_tree(nodes, expected_version_id="ver-synthetic-1")
