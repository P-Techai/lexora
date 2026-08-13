import pytest
from src.application.parsers.brazilian_law_parser import BrazilianLawParser
from src.domain.enums import LegalNodeType


def test_brazilian_law_parser_full_hierarchy():
    """Testa a decomposição determinística da hierarquia jurídica brasileira."""
    raw_text = """LEI COMPLEMENTAR Nº 116, DE 31 DE DEZEMBRO DE 2003
CAPÍTULO I
DO IMPOSTO SOBRE SERVIÇOS DE QUALQUER NATUREZA
Art. 1º O Imposto Sobre Serviços de Qualquer Natureza tem como fato gerador a prestação de serviços.
§ 1º O imposto incide também sobre o serviço proveniente do exterior.
§ 2º Ressalvadas as exceções expressas na lista anexa.
Art. 2º O imposto não incide sobre:
I - as exportações de serviços para o exterior;
II - a prestação de serviços em relação de emprego;
Parágrafo único. Não se enquadram no inciso I os serviços desenvolvidos no Brasil.
a) primeiro detalhe da alínea;
1. primeiro item numerado."""

    parser = BrazilianLawParser()
    nodes, warnings = parser.parse_structure(raw_text, version_id="ver-lc116")

    assert len(nodes) > 5

    # 1. Valida nó Raiz NORMA
    root = nodes[0]
    assert root.node_type == LegalNodeType.NORMA
    assert root.parent_id is None

    # 2. Valida Nós Filhos
    node_types = [n.node_type for n in nodes]
    assert LegalNodeType.CAPITULO in node_types
    assert LegalNodeType.ARTIGO in node_types
    assert LegalNodeType.PARAGRAFO in node_types
    assert LegalNodeType.INCISO in node_types
    assert LegalNodeType.ALINEA in node_types
    assert LegalNodeType.ITEM in node_types

    # 3. Valida Preservação do RAW TEXT e NORMALIZED TEXT
    art1 = next(n for n in nodes if n.identifier == "art-1")
    assert "Art. 1º O Imposto" in art1.text
    assert art1.normalized_text == "art 1º o imposto sobre serviços de qualquer natureza tem como fato gerador a prestação de serviços"


def test_brazilian_law_parser_zero_silent_data_loss():
    """Testa que linhas não classificadas são mantidas como nó NOTA com warning (Zero Silent Data Loss)."""
    raw_text = """DECRETO Nº 9.580, DE 22 DE DEZEMBRO DE 2018
Texto de introdução não estruturado do preâmbulo.
Art. 1º Regulamento do Imposto de Renda."""

    parser = BrazilianLawParser()
    nodes, warnings = parser.parse_structure(raw_text, version_id="ver-dec9580")

    assert len(warnings) > 0
    nota_node = next((n for n in nodes if n.node_type == LegalNodeType.NOTA), None)
    assert nota_node is not None
    assert "Texto de introdução não estruturado" in nota_node.text
