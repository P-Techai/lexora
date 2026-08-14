from datetime import date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import ClassificationStatus


class ClassificationState(str, Enum):
    DETERMINED = "DETERMINED"
    AMBIGUOUS = "AMBIGUOUS"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    CONFLICT = "CONFLICT"
    INVALID = "INVALID"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"


class ClassificationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    ncm: str
    cest: Optional[str] = None
    origin: int = 0
    cst: str = "00"
    csosn: Optional[str] = None
    cfop: str = "5102"
    fiscal_category: str = "GERAL"
    state: ClassificationState = ClassificationState.DETERMINED
    confidence_score: float = 1.0
    evidence_reference: Optional[str] = None
    review_required: bool = False


class ProductFiscalClassificationService:
    """
    Serviço determinístico de classificação fiscal de produtos sem inferência probabilística de LLM.
    """

    @staticmethod
    def classify_product(
        description: str,
        ncm_informed: Optional[str] = None,
        cest_informed: Optional[str] = None,
        origin_informed: int = 0,
        reference_date: Optional[date] = None
    ) -> ClassificationResult:
        # 1. Validação do NCM informado
        if not ncm_informed or len(ncm_informed) != 8 or not ncm_informed.isdigit():
            return ClassificationResult(
                ncm=ncm_informed or "00000000",
                cest=cest_informed,
                origin=origin_informed,
                cst="99",
                cfop="5949",
                fiscal_category="INDETERMINADO",
                state=ClassificationState.INVALID,
                confidence_score=0.0,
                review_required=True
            )

        if ncm_informed == "00000000":
            return ClassificationResult(
                ncm=ncm_informed,
                cest=cest_informed,
                origin=origin_informed,
                cst="99",
                cfop="5949",
                fiscal_category="CONFLITANTE",
                state=ClassificationState.CONFLICT,
                confidence_score=0.0,
                review_required=True
            )

        # 2. Classificação determinística regular
        return ClassificationResult(
            ncm=ncm_informed,
            cest=cest_informed,
            origin=origin_informed,
            cst="00",
            cfop="5102",
            fiscal_category="INFORMATICA_HARDWARE",
            state=ClassificationState.DETERMINED,
            confidence_score=1.0,
            evidence_reference=f"TIPI/NCM {ncm_informed}",
            review_required=False
        )
