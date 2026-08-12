from datetime import date
from typing import Optional
import uuid

from src.application.ports.repositories import (
    EvidenceRepository,
    LegalNodeRepository,
    LegalRelationRepository,
)
from src.domain.entities.legal_relation import LegalRelation
from src.domain.enums import LegalRelationType
from src.domain.exceptions import InvalidLegalNodeError, MissingEvidenceError, MissingRevokingSourceError


class RevokeLegalNodeUseCase:
    """Caso de Uso para Revogação Parcial de Dispositivos (LegalNode). NUNCA executa DELETE SQL."""

    def __init__(
        self,
        node_repo: LegalNodeRepository,
        relation_repo: LegalRelationRepository,
        evidence_repo: EvidenceRepository,
    ):
        self.node_repo = node_repo
        self.relation_repo = relation_repo
        self.evidence_repo = evidence_repo

    async def execute(
        self,
        node_id: str,
        revocation_date: date,
        evidence_id: str,
        revoking_node_id: Optional[str] = None
    ) -> bool:
        target_node = await self.node_repo.get_by_id(node_id)
        if not target_node:
            raise InvalidLegalNodeError(f"Nó com ID '{node_id}' não existe.")

        evidence = await self.evidence_repo.get_by_id(evidence_id)
        if not evidence:
            raise MissingEvidenceError(f"Evidência com ID '{evidence_id}' exigida para revogação não existe.")

        # CORREÇÃO CRÍTICA (PROMPT 06.1): A revogação exige um nó revogador distinto. Auto-relação é proibida.
        if not revoking_node_id or revoking_node_id == node_id:
            raise MissingRevokingSourceError(
                f"Revogação normativa rejeitada: revoking_node_id ({revoking_node_id}) é nulo ou idêntico ao nó alvo ({node_id}). "
                "Uma norma não pode revogar a si mesma sem um ato revogador distinto."
            )

        relation = LegalRelation(
            id=str(uuid.uuid4()),
            source_node_id=revoking_node_id,
            target_node_id=target_node.id,
            relation_type=LegalRelationType.REVOKES,
            effective_from=revocation_date,
            confidence=1.0,
            evidence_id=evidence_id
        )
        await self.relation_repo.save(relation)

        return True
