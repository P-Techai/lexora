from datetime import date
from typing import List, Tuple

from src.domain.entities.legal_version import LegalVersion
from src.domain.enums import TemporalStatus
from src.domain.exceptions import InvalidEffectivePeriodError


class TemporalIntegrityValidator:
    """Validador puro de domínio para integridade de intervalos de vigência temporal."""

    @staticmethod
    def is_date_in_range(target_date: date, effective_from: date, effective_until: date = None) -> bool:
        """
        Semântica do Intervalo Semi-Aberto: [effective_from, effective_until).
        Retorna True se target_date >= effective_from E (effective_until é None OU target_date < effective_until).
        """
        if target_date < effective_from:
            return False

        if effective_until is not None:
            return target_date < effective_until

        return True

    @classmethod
    def validate_version_period(cls, version: LegalVersion) -> None:
        """Garante que a data de início não seja posterior à data de término."""
        if version.effective_from and version.effective_until:
            if version.effective_until < version.effective_from:
                raise InvalidEffectivePeriodError(
                    f"Versão '{version.id}' possui effective_until ({version.effective_until}) "
                    f"anterior a effective_from ({version.effective_from})."
                )

    @classmethod
    def audit_version_series(cls, versions: List[LegalVersion]) -> Tuple[TemporalStatus, List[str]]:
        """
        Inspeciona uma série de versões de um mesmo documento e detecta:
        - SOBREPOSIÇÃO (OVERLAP -> TEMPORAL_CONFLICT)
        - LACUNA TEMPORAL (GAP -> TEMPORAL_GAP)
        """
        if not versions:
            return TemporalStatus.NOT_FOUND, ["Nenhuma versão fornecida para auditoria."]

        warnings: List[str] = []
        
        # 1. Validação de período individual
        for v in versions:
            cls.validate_version_period(v)

        # Ordenar versões por effective_from
        sorted_versions = sorted(
            versions,
            key=lambda v: (v.effective_from or date.min, v.version_number)
        )

        has_overlap = False
        has_gap = False

        for i in range(len(sorted_versions) - 1):
            curr = sorted_versions[i]
            nxt = sorted_versions[i + 1]

            if not curr.effective_from or not nxt.effective_from:
                continue

            # Verificação de Overlap
            # Se curr.effective_until é None, mas existe nxt com effective_from posterior -> Overlap se nxt começa antes do fim de curr
            if curr.effective_until is None:
                has_overlap = True
                warnings.append(
                    f"CONFLITO TEMPORAL: Versão {curr.version_number} possui vigência aberta (NULL), "
                    f"mas Versão {nxt.version_number} inicia em {nxt.effective_from}."
                )
            elif curr.effective_until > nxt.effective_from:
                has_overlap = True
                warnings.append(
                    f"CONFLITO TEMPORAL: Versão {curr.version_number} vigora até {curr.effective_until}, "
                    f"mas Versão {nxt.version_number} já inicia em {nxt.effective_from}."
                )

            # Verificação de Gap
            elif curr.effective_until is not None and curr.effective_until < nxt.effective_from:
                has_gap = True
                warnings.append(
                    f"GAP TEMPORAL: Lacuna sem cobertura normativa entre {curr.effective_until} "
                    f"e {nxt.effective_from} (Versões {curr.version_number} e {nxt.version_number})."
                )

        if has_overlap:
            return TemporalStatus.TEMPORAL_CONFLICT, warnings

        if has_gap:
            return TemporalStatus.TEMPORAL_GAP, warnings

        return TemporalStatus.EFFECTIVE, []
