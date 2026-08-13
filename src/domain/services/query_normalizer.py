import re
from src.domain.services.normalization_service import LegalNormalizationService


class LegalQueryNormalizer:
    """Normalizador determinístico de consultas de busca jurídica (0 uso de LLM)."""

    @staticmethod
    def normalize_query(query: str) -> str:
        """
        Normaliza a string de busca: unifica espaços, converte caixa baixa e extrai identificadores normativos padrão.
        Exemplo: "  Artigo  1º ,  inciso I  da   LC  116 " -> "artigo 1º inciso i da lc 116"
        """
        if not query or not isinstance(query, str):
            return ""

        text = query.strip()
        # Normalização Unicode NFKC e remoção de espaços duplos
        text = LegalNormalizationService.normalize_text(text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def extract_normative_identifiers(query: str) -> dict:
        """Extrai números de artigo ou norma presentes na query para pontuação de correspondência exata."""
        normalized = LegalQueryNormalizer.normalize_query(query)
        identifiers = {}

        m_art = re.search(r'art(?:igo|\.)?\s*(\d+[ºo°]?)', normalized, re.IGNORECASE)
        if m_art:
            identifiers["article_number"] = m_art.group(1)

        m_doc = re.search(r'(?:lei|lc|decreto|portaria)\s*(?:nº|n°|n)?\s*(\d+)', normalized, re.IGNORECASE)
        if m_doc:
            identifiers["document_number"] = m_doc.group(1)

        return identifiers
