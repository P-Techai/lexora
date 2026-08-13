from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from src.domain.entities.acquisition_audit_log import AcquisitionAuditLog
from src.domain.entities.raw_artifact import RawArtifact
from src.domain.entities.source import Source
from src.domain.enums import ChangeStatus


class AcquisitionRequest(BaseModel):
    """Solicitação de aquisição de artefato normativo de fonte oficial."""
    source: Source
    target_url: str
    expected_hash: Optional[str] = None
    timeout_seconds: float = Field(default=30.0, description="Tempo limite em segundos para a requisição HTTP")
    max_bytes: int = Field(default=50 * 1024 * 1024, description="Tamanho máximo de download em bytes")


class AcquisitionResult(BaseModel):
    """Resultado canônico contendo o contrato completo da operação de aquisição."""
    source_id: str
    requested_url: str
    final_url: str
    redirect_chain: List[str] = Field(default_factory=list, description="Histórico de URLs percorridas via HTTP redirect")
    redirect_count: int = 0
    http_status: int = 200
    content_type: str
    content_length: Optional[int] = None
    content_hash: str
    content_bytes: bytes
    artifact: RawArtifact
    audit_log: AcquisitionAuditLog
    change_status: ChangeStatus
    sanitized_error: Optional[str] = None
    captured_at: datetime
    timeout_seconds: float = 30.0
