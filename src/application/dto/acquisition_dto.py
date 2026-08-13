from typing import List, Optional
from pydantic import BaseModel, Field

from src.domain.entities.acquisition_audit_log import AcquisitionAuditLog
from src.domain.entities.raw_artifact import RawArtifact
from src.domain.entities.source import Source


class AcquisitionRequest(BaseModel):
    """Solicitação de aquisição de artefato normativo de fonte oficial."""
    source: Source
    target_url: str
    expected_hash: Optional[str] = None
    timeout_seconds: float = Field(default=30.0, description="Tempo limite em segundos para a requisição HTTP")
    max_bytes: int = Field(default=50 * 1024 * 1024, description="Tamanho máximo de download em bytes")


class AcquisitionResult(BaseModel):
    """Resultado canônico contendo artefato, log de auditoria, bytes e histórico de redirecionamentos."""
    artifact: RawArtifact
    audit_log: AcquisitionAuditLog
    content_bytes: bytes
    redirect_chain: List[str] = Field(default_factory=list, description="Histórico de URLs percorridas via HTTP redirect")
