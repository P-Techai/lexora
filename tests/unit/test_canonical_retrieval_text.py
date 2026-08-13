import pytest
from src.domain.entities.legal_node import LegalNode
from src.domain.enums import LegalNodeType
from src.domain.services.retrieval_text_builder import CanonicalRetrievalTextBuilder


def test_canonical_retrieval_text_builder_with_ancestors():
    """Testa a construção do texto canônico de recuperação com preservação do contexto hierárquico ancestral."""
    norma = LegalNode(
        id="n-norma", legal_version_id="v1", parent_id=None,
        node_type=LegalNodeType.NORMA, identifier="norma-raiz",
        label="LEI COMPLEMENTAR 116/2003", text="Lei Complementar 116",
        path="/norma", position=1, content_hash="h0"
    )

    capitulo = LegalNode(
        id="n-cap", legal_version_id="v1", parent_id="n-norma",
        node_type=LegalNodeType.CAPITULO, identifier="capitulo-i",
        label="CAPÍTULO I", text="DO IMPOSTO SOBRE SERVIÇOS",
        path="/norma/capitulo-i", position=2, content_hash="h1"
    )

    artigo = LegalNode(
        id="n-art1", legal_version_id="v1", parent_id="n-cap",
        node_type=LegalNodeType.ARTIGO, identifier="art-1",
        label="Art. 1º", text="O Imposto Sobre Serviços de Qualquer Natureza tem como fato gerador a prestação de serviços.",
        path="/norma/capitulo-i/art-1", position=3, content_hash="h2"
    )

    contextual_text = CanonicalRetrievalTextBuilder.build_retrieval_text(artigo, [norma, capitulo, artigo])

    assert "LEI COMPLEMENTAR 116/2003" in contextual_text
    assert "CAPÍTULO I" in contextual_text
    assert "Art. 1º: O Imposto" in contextual_text
