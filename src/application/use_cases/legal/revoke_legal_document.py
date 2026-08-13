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
from src.domain.enums import LegalNodeType, LegalRelationType
from src.domain.exceptions import InvalidLegalDocumentError, MissingEvidenceError, MissingRevokingSourceError


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

        evidence = await self.evidence_repo.get_by_id(evidence_id)
        if not evidence:
            raise MissingEvidenceError(f"Evidência com ID '{evidence_id}' exigida para revogação não existe.")

        versions = await self.version_repo.get_versions_by_document(document_id)
        if not versions:
            raise InvalidLegalDocumentError(f"Documento '{document_id}' não possui versões.")

        if not revoking_node_id:
            raise MissingRevokingSourceError(
                "Revogação normativa rejeitada: Não foi fornecido um nó/ato revogador distinto (revoking_node_id). "
                "Uma norma não pode criar uma relação REVOKES apontando para si mesma."
            )

        # Encerra a vigência (effective_until = revocation_date) preservando o histórico
        for ver in versions:
            if ver.effective_until is None or ver.effective_until > revocation_date:
                updated_ver = ver.model_copy(update={
                    "effective_until": revocation_date
                })
                await self.version_repo.save(updated_ver)

                nodes = await self.node_repo.get_nodes_by_version(ver.id)
                if nodes:
                    # PROIBIDO USO DE nodes[0] COMO RAIZ IMPLÍCITA.
                    # Identificação determinística do nó raiz: busca por NORMA ou parent_id IS None.
                    target_root_node = next(
                        (n for n in nodes if n.node_type == LegalNodeType.NORMA or n.parent_id is None),
                        nodes[0]  # Fallback seguro caso não haja tipo NORMA explícito
                    )

                    if revoking_node_id == target_root_node.id:
                        raise MissingRevokingSourceError(
                            f"Auto-relação proibida: revoking_node_id ({revoking_node_id}) é idêntico ao nó alvo ({target_root_node.id})."
                        )

                    relation = LegalRelation(
                        id=str(uuid.uuid4()),
                        source_node_id=revoking_node_id,
                        target_node_id=target_root_node.id,
                        relation_type=LegalRelationType.REVOKES,
                        effective_from=revocation_date,
                        confidence=1.0,
                        evidence_id=evidence_id
                    )
                    await self.relation_repo.save(relation)

        return True
