import os
from pathlib import Path
from typing import Optional

from src.application.ports.storage_provider import StorageProvider


class LocalStorageAdapter(StorageProvider):
    """Adaptador concreto para armazenamento de arquivos no sistema de arquivos local."""

    def __init__(self, base_path: str = "./data/storage"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    async def save_bytes(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        file_path = self.base_path / key
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(data)
        return str(file_path.absolute())

    async def get_bytes(self, key: str) -> Optional[bytes]:
        file_path = self.base_path / key
        if not file_path.exists():
            return None
        with open(file_path, "rb") as f:
            return f.read()

    async def delete(self, key: str) -> bool:
        file_path = self.base_path / key
        if file_path.exists():
            os.remove(file_path)
            return True
        return False
