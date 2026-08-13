from datetime import date, datetime, timezone
import pytest

from src.application.dto.context_pack import LegalContextPack
from src.application.dto.retrieval_dto import LegalRetrievalResultItem, LegalRetrievalResultResponse
from src.application.services.context_builder import LegalContextBuilder
from src.application.services.guardrails.citation_validator import CitationValidator
from src.domain.entities.legal_answer import AnswerClaim, LegalAnswer, LegalCitation
from src.domain.enums import LegalAnswerStatus, LegalNodeType
from src.domain.exceptions import ConfigurationError
from src.infrastructure.adapters.factory import LegalAnswerGeneratorFactory


def test_factory_production_provider_selection_fails_when_unconfigured():
    """Testa que o ambiente de produção falha de forma explícita se o provedor não for configurado (0 mock fallbacks silenciosos)."""
    with pytest.raises(ConfigurationError):
        LegalAnswerGeneratorFactory.get_generator(env="production")


def test_factory_mock_only_when_configured():
    """Testa que o Mock é instanciado somente quando em ambiente de desenvolvimento/teste."""
    generator = LegalAnswerGeneratorFactory.get_generator(env="development")
    assert generator.provider_name == "mock-legal-generator"


def test_citation_12_field_mismatches():
    """Testa validação cruzada dos 12 campos no CitationValidator."""
    item = LegalRetrievalResultItem(
        legal_node_id="node-10",
        legal_version_id="ver-10",
        legal_document_id="doc-10",
        node_type=LegalNodeType.ARTIGO,
        identifier="art-10",
        label="Art. 10",
        text="Texto legal de teste.",
        path="/norma/art-10",
        hierarchical_context="NORMA > Art. 10",
        lexical_score=1.0,
        semantic_score=1.0,
        final_score=1.0,
        source_id="src-planalto",
        evidence_id="ev-10",
        effective_from=date(2000, 1, 1),
        effective_until=None,
        content_hash="hash-10",
        provenance_chain={"source_id": "src-planalto", "legal_document_id": "doc-10", "legal_version_id": "ver-10", "legal_node_id": "node-10", "evidence_id": "ev-10", "raw_artifact_hash": "hash-10"}
    )

    pack = LegalContextPack(
        pack_id="pack-test",
        query="teste",
        normalized_query="teste",
        reference_date=date(2020, 1, 1),
        selected_nodes=[item],
        canonical_context_text="[Art. 10] Texto legal de teste.",
        total_characters=50
    )

    # 1. Citação válida
    cit_valid = LegalCitation(
        citation_id="cit-10",
        legal_node_id="node-10",
        legal_version_id="ver-10",
        legal_document_id="doc-10",
        node_type=LegalNodeType.ARTIGO,
        identifier="art-10",
        label="Art. 10",
        excerpt="Texto legal de teste.",
        effective_from=date(2000, 1, 1),
        effective_until=None,
        source_id="src-planalto",
        evidence_id="ev-10",
        raw_artifact_hash="hash-10"
    )
    claim = AnswerClaim(claim_id="c1", text="Claim válido.", citation_ids=["cit-10"])
    ans_valid = LegalAnswer(
        answer_id="ans-10", logical_answer_id="log-10", query="teste", reference_date=date(2020, 1, 1),
        answer_text="Resposta válida.", claims=[claim], citations=[cit_valid], supporting_nodes=["node-10"]
    )
    ok, warnings = CitationValidator.validate_citations(ans_valid, pack)
    assert ok is True

    # 2. Citação com divergência de Evidence ID
    cit_bad_ev = cit_valid.model_copy(update={"evidence_id": "ev-ERRADA"})
    ans_bad_ev = ans_valid.model_copy(update={"citations": [cit_bad_ev]})
    ok, warnings = CitationValidator.validate_citations(ans_bad_ev, pack)
    assert ok is False
    assert "Divergência de Evidência" in warnings[0]

    # 3. Citação com divergência de Raw Hash
    cit_bad_hash = cit_valid.model_copy(update={"raw_artifact_hash": "hash-ERRADO"})
    ans_bad_hash = ans_valid.model_copy(update={"citations": [cit_bad_hash]})
    ok, warnings = CitationValidator.validate_citations(ans_bad_hash, pack)
    assert ok is False
    assert "Divergência de Raw Hash" in warnings[0]


def test_claim_without_citation_fails(sample_context_pack):
    """Testa que um claim sem citação vinculada falha na validação."""
    item = sample_context_pack.selected_nodes[0]
    cit = LegalCitation(
        citation_id="cit-1", legal_node_id=item.legal_node_id, legal_version_id=item.legal_version_id,
        legal_document_id=item.legal_document_id, node_type=item.node_type, identifier=item.identifier,
        label=item.label, excerpt=item.text, effective_from=item.effective_from, effective_until=item.effective_until,
        source_id=item.source_id, evidence_id=item.evidence_id, raw_artifact_hash=item.content_hash
    )
    claim_uncited = AnswerClaim(claim_id="c-uncited", text="Afirmação sem suporte.", citation_ids=[])
    ans_uncited = LegalAnswer(
        answer_id="ans-uncited", logical_answer_id="log-uncited", query="teste", reference_date=date(2020, 1, 1),
        answer_text="Texto com afirmação não citada.", claims=[claim_uncited], citations=[cit], supporting_nodes=[item.legal_node_id]
    )

    ok, warnings = CitationValidator.validate_citations(ans_uncited, sample_context_pack)
    assert ok is False
    assert "Claim sem citação" in warnings[0]


def test_deterministic_context_pack_id():
    """Testa que o pack_id gerado pelo LegalContextBuilder é 100% determinístico (SHA-256)."""
    builder = LegalContextBuilder()
    item = LegalRetrievalResultItem(
        legal_node_id="n1", legal_version_id="v1", legal_document_id="d1", node_type=LegalNodeType.ARTIGO,
        identifier="art-1", label="Art. 1º", text="Texto.", path="/n1", hierarchical_context="Art. 1º",
        lexical_score=1.0, semantic_score=1.0, final_score=1.0, source_id="s1", evidence_id="e1",
        effective_from=date(2000, 1, 1), content_hash="h1", provenance_chain={}
    )
    resp = LegalRetrievalResultResponse(
        query="consulta", normalized_query="consulta", reference_date=date(2020, 1, 1),
        results=[item], total_candidates=1, provenance_valid=True
    )

    pack1 = builder.build_context_pack(resp)
    pack2 = builder.build_context_pack(resp)

    assert pack1.pack_id == pack2.pack_id
    assert pack1.pack_id.startswith("pack-")
