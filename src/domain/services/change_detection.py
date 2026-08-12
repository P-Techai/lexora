from typing import Optional

from src.domain.enums import ChangeStatus
from src.domain.services.hash_service import DocumentHashCalculator


class ChangeDetectionService:
    """Serviço determinístico de detecção de alterações em conteúdo bruto de artefatos."""

    @staticmethod
    def detect_change(
        new_content_hash: str,
        previous_content_hash: Optional[str] = None
    ) -> ChangeStatus:
        """
        Compara dois hashes de conteúdo SHA-256 e determina o status de alteração.
        Retorna ChangeStatus (NEW, UNCHANGED, CHANGED).
        """
        if not previous_content_hash:
            return ChangeStatus.NEW

        if new_content_hash.lower() == previous_content_hash.lower():
            return ChangeStatus.UNCHANGED

        return ChangeStatus.CHANGED

    @classmethod
    def compare_raw_bytes(
        cls,
        new_bytes: bytes,
        previous_content_hash: Optional[str] = None
    ) -> ChangeStatus:
        new_hash = DocumentHashCalculator.calculate_sha256(new_bytes)
        return cls.detect_change(new_hash, previous_content_hash)
