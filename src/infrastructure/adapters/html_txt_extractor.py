import re
from src.application.ports.document_extractor import DocumentExtractor, ExtractedDocumentText
from src.domain.entities.raw_artifact import RawArtifact
from src.domain.exceptions import UnsupportedContentTypeError


class HtmlTxtDocumentExtractor(DocumentExtractor):
    """Adaptador concreto para extração de texto a partir de arquivos HTML e Texto Plano (TXT)."""

    def extract_text(self, artifact: RawArtifact, content_bytes: bytes) -> ExtractedDocumentText:
        try:
            text_str = content_bytes.decode("utf-8", errors="replace")
        except Exception:
            text_str = content_bytes.decode("latin1", errors="replace")

        content_type = (artifact.content_type or "").lower()

        if "html" in content_type:
            # Remoção determinística básica de tags HTML e scripts mantendo a quebra de linha
            clean_text = re.sub(r'<script.*?>.*?</script>', '', text_str, flags=re.DOTALL | re.IGNORECASE)
            clean_text = re.sub(r'<style.*?>.*?</style>', '', clean_text, flags=re.DOTALL | re.IGNORECASE)
            clean_text = re.sub(r'<br\s*/?>', '\n', clean_text, flags=re.IGNORECASE)
            clean_text = re.sub(r'</p>', '\n', clean_text, flags=re.IGNORECASE)
            clean_text = re.sub(r'<[^>]+>', '', clean_text)
            clean_text = re.sub(r'\r\n', '\n', clean_text)
            clean_text = re.sub(r'\n{3,}', '\n\n', clean_text)
            return ExtractedDocumentText(
                raw_text=clean_text.strip(),
                content_type=artifact.content_type,
                extracted_metadata={"source_format": "html"}
            )
        elif "text" in content_type or "plain" in content_type or not content_type:
            return ExtractedDocumentText(
                raw_text=text_str.strip(),
                content_type=artifact.content_type or "text/plain",
                extracted_metadata={"source_format": "txt"}
            )
        else:
            raise UnsupportedContentTypeError(f"Tipo de conteúdo '{artifact.content_type}' não suportado pelo HtmlTxtDocumentExtractor.")
