from src.application.dto.temporal_dto import TemporalLegalResult, TemporalQueryRequest
from src.application.ports.repositories import (
    EvidenceRepository,
    LegalDocumentRepository,
    LegalNodeRepository,
    LegalRelationRepository,
    LegalVersionRepository,
)
from src.domain.enums import TemporalStatus
from src.domain.services.temporal_search_service import TemporalLegalSearchService


class QueryLegalAtDateUseCase:
    """Caso de uso para consulta e determinação determinística da Verdade Jurídica em uma data de referência T."""

    def __init__(
        self,
        doc_repo: LegalDocumentRepository,
        version_repo: LegalVersionRepository,
        node_repo: LegalNodeRepository,
        relation_repo: LegalRelationRepository,
        evidence_repo: EvidenceRepository,
    ):
        self.doc_repo = doc_repo
        self.version_repo = version_repo
        self.node_repo = node_repo
        self.relation_repo = relation_repo
        self.evidence_repo = evidence_repo

    async def execute(self, request: TemporalQueryRequest) -> TemporalLegalResult:
        doc = await self.doc_repo.get_by_id(request.document_id)
        if not doc:
            return TemporalLegalResult(
                status=TemporalStatus.NOT_FOUND,
                document_id=request.document_id,
                target_date=request.target_date,
                warnings=[f"Documento '{request.document_id}' não encontrado."]
            )

        versions = await self.version_repo.get_versions_by_document(request.document_id)
        
        # Coleta relações para avaliação de revogação por relação
        all_relations = []
        for ver in versions:
            nodes = await self.node_repo.get_nodes_by_version(ver.id)
            for n in nodes:
                rels = await self.relation_repo.get_relations_for_node(n.id)
                all_relations.extend(rels)

        status, version, warnings = TemporalLegalSearchService.resolve_version_at_date(
            versions, request.target_date, relations=all_relations
        )

        if status not in (TemporalStatus.EFFECTIVE, TemporalStatus.REVOKED) or not version:
            return TemporalLegalResult(
                status=status,
                document_id=request.document_id,
                target_date=request.target_date,
                warnings=warnings
            )

        nodes = []
        relations = []
        evidences = []

        if request.include_nodes and version:
            raw_nodes = await self.node_repo.get_nodes_by_version(version.id)
            # Garante consistência de versão e filtra nós revogados na target_date
            nodes = TemporalLegalSearchService.filter_nodes_tree_consistency(
                raw_nodes, version.id, target_date=request.target_date, relations=all_relations
            )

        if request.include_relations and nodes:
            node_ids = [n.id for n in nodes]
            for nid in node_ids:
                rels = await self.relation_repo.get_relations_for_node(nid)
                relations.extend(rels)
                for r in rels:
                    if r.evidence_id:
                        ev = await self.evidence_repo.get_by_id(r.evidence_id)
                        if ev and ev not in evidences:
                            evidences.append(ev)

        return TemporalLegalResult(
            status=status,
            document_id=request.document_id,
            target_date=request.target_date,
            version_id=version.id if version else None,
            version=version,
            effective_from=version.effective_from if version else None,
            effective_until=version.effective_until if version else None,
            nodes=nodes,
            relations=relations,
            evidences=evidences,
            warnings=warnings
        )
