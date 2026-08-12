import re
import unicodedata


class LegalNormalizationService:
    """Serviço puro de normalização de texto sem alterar o conteúdo nem o significado jurídico original."""

    @staticmethod
    def normalize_text(text: str) -> str:
        if not text:
            return ""

        # 1. Normalização Unicode NFKC para padronização de caracteres e acentos
        normalized = unicodedata.normalize("NFKC", text)

        # 2. Substituição de quebras de linha NUL ou estranhas por \n padrão
        normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")

        # 3. Substituição de múltiplos espaços em branco no mesmo parágrafo por um único espaço
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in normalized.split("\n")]

        # 4. Junção com quebra de linha limpa
        return "\n".join(lines).strip()
