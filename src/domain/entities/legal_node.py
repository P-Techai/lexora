from datetime import date
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict

from src.domain.enums import LegalNodeType, NodeStatus


class LegalNode(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    norma_id: str
    node_type: LegalNodeType
    number: str
    text: str
    parent_id: Optional[str] = None
    path: str
    position: int
    metadata: Dict[str, Any] = Field(default_factory=dict)
    effective_from: date
    effective_until: Optional[date] = None
    version: int = 1
    status: NodeStatus = NodeStatus.ACTIVE
    content_hash: str

    def is_effective_on(self, target_date: date) -> bool:
        """Verifica se o dispositivo estava juridicamente vigente na data informada."""
        if target_date < self.effective_from:
            return False
        if self.effective_until is not None and target_date > self.effective_until:
            return False
        return self.status == NodeStatus.ACTIVE
