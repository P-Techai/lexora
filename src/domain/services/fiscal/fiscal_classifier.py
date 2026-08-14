import uuid
from typing import List, Optional

from src.domain.enums import ClassificationStatus
from src.domain.fiscal.fiscal_classification import FiscalClassification
from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.fiscal.fiscal_product import FiscalProductProfile
from src.domain.services.fiscal.fiscal_normalizer import FiscalNormalizer


class FiscalClassifier:
    """
    Classificador determinístico de NCM, CST, CFOP e perfil de fatos fiscais.
    NUNCA trata UNKNOWN como CONFIRMED. Retorna REVIEW_REQUIRED para ambiguidades.
    """

    @staticmethod
    def classify_product(product: FiscalProductProfile) -> FiscalClassification:
        """
        Classifica um perfil de produto.
        """
        reasons: List[str] = []
        normalized_ncm = FiscalNormalizer.normalize_ncm(product.ncm)

        if not normalized_ncm or len(normalized_ncm) != 8:
            reasons.append("NCM ausente ou com tamanho inválido (diferente de 8 dígitos).")
            return FiscalClassification(
                classification_id=f"class_{uuid.uuid4().hex[:8]}",
                ncm=product.ncm or "",
                cst=None,
                cfop=None,
                status=ClassificationStatus.REVIEW_REQUIRED,
                reasons=reasons
            )

        if product.classification_status == ClassificationStatus.CONFIRMED:
            reasons.append("Classificação previamente confirmada por evidência legal ou humana.")
            return FiscalClassification(
                classification_id=f"class_{uuid.uuid4().hex[:8]}",
                ncm=normalized_ncm,
                cst=None,
                cfop=None,
                status=ClassificationStatus.CONFIRMED,
                reasons=reasons
            )

        if product.classification_status == ClassificationStatus.PROVISIONAL:
            reasons.append("Classificação provisória aguardando revisão normativa.")
            return FiscalClassification(
                classification_id=f"class_{uuid.uuid4().hex[:8]}",
                ncm=normalized_ncm,
                cst=None,
                cfop=None,
                status=ClassificationStatus.PROVISIONAL,
                reasons=reasons
            )

        if product.classification_status == ClassificationStatus.UNKNOWN:
            reasons.append("Status de classificação do produto é UNKNOWN.")
            return FiscalClassification(
                classification_id=f"class_{uuid.uuid4().hex[:8]}",
                ncm=normalized_ncm,
                cst=None,
                cfop=None,
                status=ClassificationStatus.REVIEW_REQUIRED,
                reasons=reasons
            )

        return FiscalClassification(
            classification_id=f"class_{uuid.uuid4().hex[:8]}",
            ncm=normalized_ncm,
            cst=None,
            cfop=None,
            status=product.classification_status,
            reasons=reasons
        )

    @staticmethod
    def classify_fact(fact: FiscalFact) -> FiscalClassification:
        """
        Classifica o fato fiscal verificando NCM, CST e CFOP.
        """
        reasons: List[str] = []
        ncm = FiscalNormalizer.normalize_ncm(fact.ncm)
        cst = FiscalNormalizer.normalize_cst(fact.cst)
        cfop = FiscalNormalizer.normalize_cfop(fact.cfop)

        status = ClassificationStatus.CONFIRMED

        if not ncm or len(ncm) != 8:
            reasons.append("NCM ausente ou inválido.")
            status = ClassificationStatus.REVIEW_REQUIRED

        if not cst:
            reasons.append("CST/CSOSN ausente.")
            status = ClassificationStatus.REVIEW_REQUIRED

        if not cfop:
            reasons.append("CFOP ausente.")
            status = ClassificationStatus.REVIEW_REQUIRED

        if status == ClassificationStatus.CONFIRMED:
            reasons.append("Fato fiscal completo com NCM, CST e CFOP válidos.")

        return FiscalClassification(
            classification_id=f"class_fact_{uuid.uuid4().hex[:8]}",
            ncm=ncm or fact.ncm or "",
            cst=cst,
            cfop=cfop,
            status=status,
            reasons=reasons
        )
