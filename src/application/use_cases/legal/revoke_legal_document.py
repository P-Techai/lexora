from datetime import date
from typing import Optional
import uuid

from src.application.ports.repositories import (
    EvidenceRepository,
    LegalDocumentRepository,
    LegalNodeRepository,
    LegalRelationRepository,
    LegalVersionRepository,
)
from src.domain.entities.legal_relation import LegalRelation
from src.domain.enums import LegalRelationType, VersionStatus
from src.domain.exceptions import InvalidLegalDocumentError, MissingEvidenceError


class RevokeLegalDocumentUseCase:
    """Caso de Uso para Revogação Total de Documentos Normativos. A revogação NUNCA é um DELETE SQL."""

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

    async def execute(
        self,
        document_id: str,
        revocation_date: date,
        evidence_id: str,
        revoking_node_id: Optional[str] = None
    ) -> bool:
        doc = await self.doc_repo.get_by_id(document_id)
        if not doc:
            raise InvalidLegalDocumentError(f"Documento com ID '{document_id}' não existe.")

        # Evidência é obrigatória para revogação
        evidence = await self.evidence_repo.get_by_id(evidence_id)
        if not evidence:
            raise MissingEvidenceError(f"Evidência com ID '{evidence_id}' exigida para revogação não existe.")

        versions = await self.version_repo.get_versions_by_document(document_id)
        if not versions:
            raise InvalidLegalDocumentError(f"Documento '{document_id}' não possui versões.")

        # Encerra o período de vigência (effective_until = revocation_date)
        # IMPORTANTE: Preserva o histórico! Não muta o status estático da versão para REVOKED,
        # permitindo que consultas anteriores a revocation_date continuem retornando a versão vigente!
        for ver in versions:
            if ver.effective_until is None or ver.effective_until > revocation_date:
                updated_ver = ver.model_copy(update={
                    "effective_until": revocation_date
                })
                await self.version_repo.save(updated_ver)

                # Criação da Relação de Revogação vinculada à Evidência
                nodes = await self.node_repo.get_nodes_by_version(ver.id)
                if nodes:
                    target_root_node = nodes[0]
                    relation = LegalRelation(
                        id=str(uuid.uuid4()),
                        source_node_id=revoking_node_id or target_root_node.id,
                        target_node_id=target_root_node.id,
                        relation_type=LegalRelationType.REVOKES,
                        effective_from=revocation_date,
                        confidence=1.0,
                        evidence_id=evidence_id
                    )
                    await self.relation_repo.save(relation)

        return True
