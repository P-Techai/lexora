import uuid
from datetime import datetime, timezone
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict, Field

from src.domain.decision.decision import Decision
from src.domain.services.fiscal.fiscal_diff_engine import FiscalDiffEngine


class ReprocessingRun(BaseModel):
    """
    Registro auditável de execução de reprocessamento histórico de decisão fiscal.
    """
    model_config = ConfigDict(frozen=True)

    reprocessing_id: str = Field(..., description="ID único da execução de reprocessamento")
    source_decision_id: str = Field(..., description="ID da decisão fiscal original intacta")
    new_decision_id: str = Field(..., description="ID da nova decisão fiscal resultante")
    old_engine_version: str = Field(..., description="Versão do motor na decisão original")
    new_engine_version: str = Field(..., description="Versão do motor no reprocessamento")
    reason: str = Field(..., description="Justificativa do reprocessamento")
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ReprocessingService:
    """
    Serviço de reprocessamento histórico sem alteração destrutiva.
    """

    @staticmethod
    def execute_reprocessing(
        old_decision: Decision,
        new_decision: Decision,
        reason: str,
        new_engine_version: str = "v0.12.0-fiscal-classification-tax-engine"
    ) -> Tuple[ReprocessingRun, Dict[str, Any]]:
        run = ReprocessingRun(
            reprocessing_id=f"reproc_{uuid.uuid4().hex[:8]}",
            source_decision_id=old_decision.decision_id,
            new_decision_id=new_decision.decision_id,
            old_engine_version=old_decision.decision_trace.get("engine_version", "v0.10.0-fiscal-brain-foundation"),
            new_engine_version=new_engine_version,
            reason=reason
        )

        diff = FiscalDiffEngine.compare_decisions(old_decision, new_decision)
        return run, diff
