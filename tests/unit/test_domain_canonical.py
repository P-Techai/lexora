from datetime import date, datetime
import sys
from typing import List
import pytest

from src.domain.entities.evidence import Evidence
from src.domain.entities.legal_document import LegalDocument
from src.domain.entities.legal_node import LegalNode
from src.domain.entities.legal_relation import LegalRelation
from src.domain.entities.legal_version import LegalVersion
from src.domain.entities.source import Source
from src.domain.enums import (
    DocumentType,
    Jurisdiction,
    LegalNodeType,
    LegalRelationType,
    NodeStatus,
    VersionStatus,
)


def test_source_entity_authority_level():
    src = Source(
        id="src-planalto",
        name="Presidência da República - Planalto",
        official=True,
        authority_level=1,
        base_url="https://www.planalto.gov.br",
        jurisdiction=Jurisdiction.FEDERAL,
        active=True
    )
    assert src.name == "Presidência da República - Planalto"
    assert src.authority_level == 1
    assert src.official is True


def test_legal_version_temporal_validity_ranges():
    """
    Testa o requisito explícito de vigência:
    Version A: 2020-01-01 -> 2022-12-31
    Version B: 2023-01-01 -> NULL
    Testes em: 2019, 2020, 2022, 2023, 2030 e limites exatos.
    """
    ver_a = LegalVersion(
        id="ver-a",
        legal_document_id="doc-lei-8112",
        version_number=1,
        content_hash="hash-ver-a",
        effective_from=date(2020, 1, 1),
        effective_until=date(2022, 12, 31),
        status=VersionStatus.ACTIVE
    )

    ver_b = LegalVersion(
        id="ver-b",
        legal_document_id="doc-lei-8112",
        version_number=2,
        content_hash="hash-ver-b",
        effective_from=date(2023, 1, 1),
        effective_until=None,
        status=VersionStatus.ACTIVE
    )

    # Ano 2019: nenhuma versão ativa
    assert ver_a.is_effective_on(date(2019, 12, 31)) is False
    assert ver_b.is_effective_on(date(2019, 12, 31)) is False

    # Ano 2020: Versão A ativa
    assert ver_a.is_effective_on(date(2020, 1, 1)) is True
    assert ver_b.is_effective_on(date(2020, 1, 1)) is False

    # Ano 2022 (limite superior da A): Versão A ativa
    assert ver_a.is_effective_on(date(2022, 12, 31)) is True
    assert ver_b.is_effective_on(date(2022, 12, 31)) is False

    # Ano 2023 (início da B): Versão A inativa, Versão B ativa
    assert ver_a.is_effective_on(date(2023, 1, 1)) is False
    assert ver_b.is_effective_on(date(2023, 1, 1)) is True

    # Ano 2030: Versão B ativa (aberta)
    assert ver_a.is_effective_on(date(2030, 6, 15)) is False
    assert ver_b.is_effective_on(date(2030, 6, 15)) is True


def test_legal_node_hierarchy_tree_and_position():
    """
    Testa árvore hierárquica e ordenação por posição:
    Art. 1º
    ├── § 1º (position: 1)
    ├── § 2º (position: 2)
    └── Inciso I (position: 3)
    """
    art_1 = LegalNode(
        id="node-art-1",
        legal_version_id="ver-a",
        parent_id=None,
        node_type=LegalNodeType.ARTIGO,
        identifier="art-1",
        label="Art. 1º",
        text="Texto do artigo primeiro...",
        path="/art-1",
        position=1,
        content_hash="hash-art1"
    )

    par_1 = LegalNode(
        id="node-par-1",
        legal_version_id="ver-a",
        parent_id="node-art-1",
        node_type=LegalNodeType.PARAGRAFO,
        identifier="par-1",
        label="§ 1º",
        text="Texto do parágrafo primeiro...",
        path="/art-1/par-1",
        position=1,
        content_hash="hash-par1"
    )

    par_2 = LegalNode(
        id="node-par-2",
        legal_version_id="ver-a",
        parent_id="node-art-1",
        node_type=LegalNodeType.PARAGRAFO,
        identifier="par-2",
        label="§ 2º",
        text="Texto do parágrafo segundo...",
        path="/art-1/par-2",
        position=2,
        content_hash="hash-par2"
    )

    inc_1 = LegalNode(
        id="node-inc-1",
        legal_version_id="ver-a",
        parent_id="node-art-1",
        node_type=LegalNodeType.INCISO,
        identifier="inc-1",
        label="Inciso I",
        text="Texto do inciso primeiro...",
        path="/art-1/inc-1",
        position=3,
        content_hash="hash-inc1"
    )

    children: List[LegalNode] = [inc_1, par_1, par_2]
    sorted_children = sorted(children, key=lambda n: n.position)

    assert sorted_children[0].label == "§ 1º"
    assert sorted_children[1].label == "§ 2º"
    assert sorted_children[2].label == "Inciso I"
    assert par_1.parent_id == art_1.id


def test_legal_relation_amends():
    """Testa relação normativa (ex: Norma B AMENDS Norma A) com evidência."""
    evidence = Evidence(
        id="ev-001",
        source_id="src-planalto",
        quote_or_excerpt="Altera o caput do art. 1º da Lei nº 8.112/1990",
        content_hash="hash-ev-1",
        captured_at=datetime.utcnow()
    )

    relation = LegalRelation(
        id="rel-001",
        source_node_id="node-art-1-lei-b",
        target_node_id="node-art-1-lei-a",
        relation_type=LegalRelationType.AMENDS,
        confidence=1.0,
        evidence_id=evidence.id
    )

    assert relation.source_node_id != relation.target_node_id
    assert relation.relation_type == LegalRelationType.AMENDS
    assert relation.evidence_id == "ev-001"


def test_domain_portability_audit():
    """
    Verifica que nenhum módulo do src/domain importa SQLAlchemy, psycopg ou drivers de banco.
    """
    domain_modules = [mod for mod in sys.modules if mod.startswith("src.domain")]
    forbidden_keywords = ["sqlalchemy", "psycopg", "asyncpg", "supabase", "cloudflare"]

    for mod_name in domain_modules:
        module = sys.modules[mod_name]
        mod_dict = getattr(module, "__dict__", {})
        for key in mod_dict:
            val_str = str(mod_dict[key]).lower()
            for forbidden in forbidden_keywords:
                assert forbidden not in val_str, f"Injeção indevida de '{forbidden}' encontrada em '{mod_name}.{key}'"
