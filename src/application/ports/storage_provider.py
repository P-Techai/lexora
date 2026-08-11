from abc import ABC, abstractmethod
from typing import Optional


class StorageProvider(ABC):
    """Porta abstrata para armazenamento de arquivos (S3, Cloudflare R2, Local)."""

    @abstractmethod
    async def save_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Salva um conjunto de bytes no repositório de arquivos e retorna a URI ou chave."""
        pass

    @abstractmethod
    async def get_bytes(self, key: str) -> Optional[bytes]:
        """Recupera os bytes de um arquivo armazenado."""
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Remove um arquivo do repositório de armazenagem."""
        pass
