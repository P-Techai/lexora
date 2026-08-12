from datetime import date
from typing import List, Optional, Tuple

from src.domain.entities.legal_node import LegalNode
from src.domain.entities.legal_relation import LegalRelation
from src.domain.entities.legal_version import LegalVersion
from src.domain.enums import LegalRelationType, TemporalStatus, VersionStatus
from src.domain.services.temporal_validator import TemporalIntegrityValidator


class TemporalLegalSearchService:
    """Serviço de busca e determinação determinística da Verdade Jurídica em uma data de referência T."""

    @classmethod
    def resolve_version_at_date(
        cls,
        versions: List[LegalVersion],
        target_date: date,
        relations: Optional[List[LegalRelation]] = None
    ) -> Tuple[TemporalStatus, Optional[LegalVersion], List[str]]:
        """
        Determina qual versão de um documento jurídico estava vigente na target_date.
        Aplica a semântica de intervalo semi-aberto [effective_from, effective_until).
        A revogação é avaliada DINAMICAMENTE em relação a target_date (preservando o histórico prévio!).
        """
        if not versions:
            return TemporalStatus.NOT_FOUND, None, ["Documento não possui versões registradas."]

        # 1. Auditoria de sobreposição / gaps na série temporal
        series_status, series_warnings = TemporalIntegrityValidator.audit_version_series(versions)
        if series_status == TemporalStatus.TEMPORAL_CONFLICT:
            return TemporalStatus.TEMPORAL_CONFLICT, None, series_warnings

        # 2. Filtragem da versão aplicável à target_date
        applicable_versions: List[LegalVersion] = []
        expired_versions: List[LegalVersion] = []

        for version in versions:
            if version.effective_from:
                if TemporalIntegrityValidator.is_date_in_range(
                    target_date, version.effective_from, version.effective_until
                ):
                    applicable_versions.append(version)
                elif version.effective_until and target_date >= version.effective_until:
                    expired_versions.append(version)

        if not applicable_versions:
            # Se target_date é após o encerramento de vigência por revogação
            if expired_versions:
                last_expired = max(expired_versions, key=lambda v: v.effective_until or date.max)
                # Verifica se há relação de revogação eficaz em target_date
                is_revoked_by_relation = False
                if relations:
                    for rel in relations:
                        if rel.relation_type == LegalRelationType.REVOKES and rel.effective_from and target_date >= rel.effective_from:
                            is_revoked_by_relation = True
                            break
                
                if last_expired.status == VersionStatus.REVOKED or is_revoked_by_relation or last_expired.effective_until:
                    return TemporalStatus.REVOKED, last_expired, [f"A versão {last_expired.version_number} foi revogada em {last_expired.effective_until}."]
                return TemporalStatus.EXPIRED, last_expired, [f"A versão {last_expired.version_number} expirou em {last_expired.effective_until}."]

            # Verifica Vacatio Legis
            earliest_from = min((v.effective_from for v in versions if v.effective_from), default=None)
            if earliest_from and target_date < earliest_from:
                return TemporalStatus.NOT_YET_EFFECTIVE, None, [f"A norma ainda não estava em vigor na data {target_date} (vigência inicia em {earliest_from})."]

            return TemporalStatus.EXPIRED, None, [f"Nenhuma versão vigente encontrada para a data {target_date}."]

        if len(applicable_versions) > 1:
            return TemporalStatus.TEMPORAL_CONFLICT, None, ["Múltiplas versões encontradas para a mesma data (conflito temporal)."]

        selected_version = applicable_versions[0]

        # Verifica se há revogação dinâmica via relação eficaz na data
        if relations:
            for rel in relations:
                if rel.relation_type == LegalRelationType.REVOKES and rel.effective_from and target_date >= rel.effective_from:
                    return TemporalStatus.REVOKED, selected_version, [f"O documento foi revogado com efeitos a partir de {rel.effective_from}."]

        return TemporalStatus.EFFECTIVE, selected_version, []

    @classmethod
    def filter_nodes_tree_consistency(
        cls,
        nodes: List[LegalNode],
        expected_version_id: str,
        target_date: Optional[date] = None,
        relations: Optional[List[LegalRelation]] = None
    ) -> List[LegalNode]:
        """
        Garante a consistência de versão da árvore normativa em uma consulta temporal.
        Se target_date e relações de revogação forem fornecidos, avalia revogação parcial por nó.
        """
        version_nodes = [node for node in nodes if node.legal_version_id == expected_version_id]
        if not target_date or not relations:
            return version_nodes

        revoked_node_ids = set()
        for rel in relations:
            if rel.relation_type == LegalRelationType.REVOKES and rel.effective_from and target_date >= rel.effective_from:
                revoked_node_ids.add(rel.target_node_id)

        # Exclui nós que foram revogados na/antes da target_date
        return [node for node in version_nodes if node.id not in revoked_node_ids]
