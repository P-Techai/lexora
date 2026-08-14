from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class FiscalEvidence(BaseModel):
    """
    Vínculo de evidência jurídica entre a regra fiscal e a legislação canônica.
    """
    model_config = ConfigDict(frozen=True)

    fiscal_evidence_id: str = Field(..., description="ID da evidência fiscal")
    rule_id: str = Field(..., description="ID da regra fiscal vinculada")
    source_legal_node_id: str = Field(..., description="Nó normativo legal da fonte")
    source_legal_version_id: str = Field(..., description="Versão normativa legal da fonte")
    evidence_id: str = Field(..., description="ID da evidência jurídica auditada")
    excerpt: str = Field(..., description="Trecho literal da norma")
    raw_artifact_hash: str = Field(..., description="Hash do artefato bruto oficial")
