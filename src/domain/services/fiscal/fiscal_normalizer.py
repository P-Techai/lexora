import re
from typing import Optional


class FiscalNormalizer:
    """
    Serviço de normalização de dados fiscais (NCM, CFOP, CST, UF, descrições).
    """

    @staticmethod
    def normalize_ncm(ncm: Optional[str]) -> Optional[str]:
        """Normaliza código NCM removendo pontos e mantendo apenas dígitos."""
        if not ncm:
            return None
        clean = re.sub(r"\D", "", ncm.strip())
        if len(clean) == 8:
            return clean
        return clean if clean else None

    @staticmethod
    def normalize_cfop(cfop: Optional[str]) -> Optional[str]:
        """Normaliza código CFOP removendo pontuação."""
        if not cfop:
            return None
        clean = re.sub(r"\D", "", cfop.strip())
        return clean if clean else None

    @staticmethod
    def normalize_cst(cst: Optional[str]) -> Optional[str]:
        """Normaliza código CST/CSOSN."""
        if not cst:
            return None
        clean = re.sub(r"\D", "", cst.strip())
        return clean.zfill(2) if len(clean) <= 2 else clean

    @staticmethod
    def normalize_state(state: Optional[str]) -> Optional[str]:
        """Normaliza sigla de UF para maiúsculo com 2 caracteres."""
        if not state:
            return None
        clean = state.strip().upper()
        return clean if len(clean) == 2 else clean

    @staticmethod
    def normalize_description(text: str) -> str:
        """Normaliza descrição de produto/serviço para letras maiúsculas e espaços simples."""
        if not text:
            return ""
        text = text.upper().strip()
        text = re.sub(r"\s+", " ", text)
        return text
