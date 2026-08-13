from datetime import date, datetime
from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import LegalNodeType, NodeStatus


class LegalNode(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    legal_version_id: str
    parent_id: Optional[str] = None
    node_type: LegalNodeType
    identifier: str  # Ex: "art-1", "par-1", "inc-I"
    label: str       # Ex: "Art. 1º", "§ 1º", "Inciso I"
    text: str
    normalized_text: Optional[str] = None
    path: str        # Ex: "/art-1/par-1/inc-I"
    position: int = 1 # Ordem ordinal do nó dentro do nó pai
    content_hash: str
    effective_from: Optional[date] = None
    effective_until: Optional[date] = None
    status: NodeStatus = NodeStatus.ACTIVE
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def logical_id(self) -> str:
        """
        Identidade Lógica Canônica Determinística do dispositivo normativo.
        Independe de UUIDs aleatórios gerados no banco.
        Formato: '{legal_version_id}:{path}'
        """
        return f"{self.legal_version_id}:{self.path}"

    def is_effective_on(self, target_date: date) -> bool:
        """Verifica se o nó normativo estava juridicamente vigente na data informada."""
        if self.status != NodeStatus.ACTIVE:
            return False
        if self.effective_from is not None and target_date < self.effective_from:
            return False
        if self.effective_until is not None and target_date > self.effective_until:
            return False
        return True
