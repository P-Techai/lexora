import uuid
from typing import Optional

from src.application.ports.repositories import EvidenceRepository, LegalNodeRepository, LegalRelationRepository
from src.domain.entities.legal_relation import LegalRelation
from src.domain.enums import LegalRelationType
from src.domain.exceptions import InvalidLegalNodeError, MissingEvidenceError


class CreateLegalRelationUseCase:
    """Caso de uso para criar e validar uma relação normativa entre dois nós com suporte a evidência."""

    def __init__(
        self,
        relation_repo: LegalRelationRepository,
        node_repo: LegalNodeRepository,
        evidence_repo: EvidenceRepository
    ):
        self.relation_repo = relation_repo
        self.node_repo = node_repo
        self.evidence_repo = evidence_repo

    async def execute(
        self,
        source_node_id: str,
        target_node_id: str,
        relation_type: LegalRelationType,
        confidence: float = 1.0,
        evidence_id: Optional[str] = None,
        effective_from=None,
        effective_until=None
    ) -> LegalRelation:
        if source_node_id == target_node_id:
            raise InvalidLegalNodeError("source_node_id e target_node_id devem ser distintos.")

        source_node = await self.node_repo.get_by_id(source_node_id)
        if not source_node:
            raise InvalidLegalNodeError(f"Nó de origem '{source_node_id}' não existe.")

        target_node = await self.node_repo.get_by_id(target_node_id)
        if not target_node:
            raise InvalidLegalNodeError(f"Nó de destino '{target_node_id}' não existe.")

        # Relações de alteração/revogação exigem proveniência de evidência
        if relation_type in (LegalRelationType.AMENDS, LegalRelationType.REVOKES) and not evidence_id:
            raise MissingEvidenceError(f"Relação do tipo '{relation_type.value}' exige obrigatoriamente um evidence_id.")

        if evidence_id:
            evidence = await self.evidence_repo.get_by_id(evidence_id)
            if not evidence:
                raise MissingEvidenceError(f"Evidência com ID '{evidence_id}' não existe.")

        relation = LegalRelation(
            id=str(uuid.uuid4()),
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            relation_type=relation_type,
            effective_from=effective_from,
            effective_until=effective_until,
            confidence=confidence,
            evidence_id=evidence_id
        )

        return await self.relation_repo.save(relation)
