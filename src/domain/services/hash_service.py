import hashlib
from typing import Union


class DocumentHashCalculator:
    """Calculador determinístico de hashes criptográficos SHA-256 para integridade e auditoria."""

    @staticmethod
    def calculate_sha256(content: Union[str, bytes]) -> str:
        """Calcula o hash SHA-256 de uma string ou bytes de conteúdo de forma determinística."""
        if isinstance(content, str):
            content_bytes = content.encode("utf-8")
        else:
            content_bytes = content

        return hashlib.sha256(content_bytes).hexdigest()
