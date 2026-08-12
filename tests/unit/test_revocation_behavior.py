from datetime import date
import pytest

from src.application.use_cases.legal.revoke_legal_document import RevokeLegalDocumentUseCase
from src.application.use_cases.legal.revoke_legal_node import RevokeLegalNodeUseCase
from src.domain.entities.evidence import Evidence
from src.domain.entities.legal_document import LegalDocument
from src.domain.entities.legal_node import LegalNode
from src.domain.entities.legal_version import LegalVersion
from src.domain.enums import DocumentType, Jurisdiction, LegalNodeType, LegalRelationType
from src.domain.exceptions import MissingRevokingSourceError


class MockRepo:
    def __init__(self):
        self.data = {}

    async def get_by_id(self, item_id):
        return self.data.get(item_id)

    async def save(self, item):
        self.data[item.id] = item
        return item

    async def save_bulk(self, items):
        for item in items:
            self.data[item.id] = item
        return items

    async def get_versions_by_document(self, doc_id):
        return [v for v in self.data.values() if isinstance(v, LegalVersion) and v.legal_document_id == doc_id]

    async def get_nodes_by_version(self, ver_id):
        return [n for n in self.data.values() if isinstance(n, LegalNode) and n.legal_version_id == ver_id]

    async def get_relations_for_node(self, node_id):
        return [r for r in self.data.values() if hasattr(r, "target_node_id") and r.target_node_id == node_id]


@pytest.mark.asyncio
async def test_scenario_a_missing_revoking_source():
    """CENÁRIO A: revoking_node_id é None -> Lança MissingRevokingSourceError."""
    doc_repo = MockRepo()
    ver_repo = MockRepo()
    node_repo = MockRepo()
    rel_repo = MockRepo()
    ev_repo = MockRepo()

    await doc_repo.save(LegalDocument(id="doc-a", source_id="src-1", document_type=DocumentType.ORDINARY_LAW, document_number="1", title="A", jurisdiction=Jurisdiction.FEDERAL, issuing_body="PRES", document_hash="h1"))
    await ver_repo.save(LegalVersion(id="ver-a", legal_document_id="doc-a", version_number=1, content_hash="h1", effective_from=date(2020, 1, 1)))
    await ev_repo.save(Evidence(id="ev-1", source_id="src-1", captured_at=date(2024, 1, 1)))

    node_uc = RevokeLegalNodeUseCase(node_repo, rel_repo, ev_repo)
    doc_uc = RevokeLegalDocumentUseCase(doc_repo, ver_repo, node_repo, rel_repo, ev_repo)

    # Rejeita revogação de nó sem revoking_node_id
    with pytest.raises(MissingRevokingSourceError):
        await node_uc.execute(node_id="node-a", revocation_date=date(2024, 1, 1), evidence_id="ev-1", revoking_node_id=None)

    # Rejeita revogação de documento sem revoking_node_id
    with pytest.raises(MissingRevokingSourceError):
        await doc_uc.execute(document_id="doc-a", revocation_date=date(2024, 1, 1), evidence_id="ev-1", revoking_node_id=None)


@pytest.mark.asyncio
async def test_scenario_b_auto_revocation_prohibited():
    """CENÁRIO B: Auto-revogação (target_node == revoking_node) -> Lança MissingRevokingSourceError."""
    node_repo = MockRepo()
    rel_repo = MockRepo()
    ev_repo = MockRepo()

    node_a = LegalNode(id="node-a", legal_version_id="ver-a", node_type=LegalNodeType.ARTIGO, identifier="art-1", label="Art. 1", text="T", path="/art-1", position=1, content_hash="ha")
    await node_repo.save(node_a)
    await ev_repo.save(Evidence(id="ev-1", source_id="src-1", captured_at=date(2024, 1, 1)))

    node_uc = RevokeLegalNodeUseCase(node_repo, rel_repo, ev_repo)

    # Tentar revogar node-a passando node-a como revogador
    with pytest.raises(MissingRevokingSourceError):
        await node_uc.execute(node_id="node-a", revocation_date=date(2024, 1, 1), evidence_id="ev-1", revoking_node_id="node-a")


@pytest.mark.asyncio
async def test_scenario_c_valid_revocation():
    """CENÁRIO C: Revogação válida (revoking_node B != target_node A) -> Cria B REVOKES A."""
    node_repo = MockRepo()
    rel_repo = MockRepo()
    ev_repo = MockRepo()

    node_a = LegalNode(id="node-a", legal_version_id="ver-a", node_type=LegalNodeType.ARTIGO, identifier="art-1", label="Art. 1", text="T", path="/art-1", position=1, content_hash="ha")
    node_b = LegalNode(id="node-b", legal_version_id="ver-b", node_type=LegalNodeType.ARTIGO, identifier="art-1", label="Art. 1", text="T", path="/art-1", position=1, content_hash="hb")

    await node_repo.save_bulk([node_a, node_b])
    await ev_repo.save(Evidence(id="ev-1", source_id="src-1", captured_at=date(2024, 1, 1)))

    node_uc = RevokeLegalNodeUseCase(node_repo, rel_repo, ev_repo)
    success = await node_uc.execute(node_id="node-a", revocation_date=date(2024, 1, 1), evidence_id="ev-1", revoking_node_id="node-b")

    assert success is True
    saved_rels = list(rel_repo.data.values())
    assert len(saved_rels) == 1
    rel = saved_rels[0]
    assert rel.source_node_id == "node-b"
    assert rel.target_node_id == "node-a"
    assert rel.relation_type == LegalRelationType.REVOKES
    assert rel.source_node_id != rel.target_node_id
