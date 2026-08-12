from typing import Optional

from src.domain.entities.legal_document import LegalDocument
from src.domain.enums import DocumentType, IdentityMatchStatus, Jurisdiction


class DocumentIdentityMatcher:
    """Serviço puro e determinístico para identificação e correspondência de documentos jurídicos sem o uso de LLMs."""

    @staticmethod
    def match_document_identity(
        doc_a: LegalDocument,
        source_id: str,
        document_type: DocumentType,
        document_number: str,
        jurisdiction: Jurisdiction,
        issuing_body: Optional[str] = None
    ) -> IdentityMatchStatus:
        """
        Avalia se a solicitação possui a mesma identidade jurídica de um documento cadastrado.
        Retorna EXACT_MATCH, POSSIBLE_MATCH ou NO_MATCH.
        """
        clean_num_a = doc_a.document_number.strip().lower()
        clean_num_b = document_number.strip().lower()

        # Se número, tipo e jurisdição forem idênticos
        if (
            doc_a.document_type == document_type
            and doc_a.jurisdiction == jurisdiction
            and clean_num_a == clean_num_b
        ):
            if doc_a.source_id == source_id:
                if issuing_body and doc_a.issuing_body.strip().lower() == issuing_body.strip().lower():
                    return IdentityMatchStatus.EXACT_MATCH
                return IdentityMatchStatus.EXACT_MATCH
            
            # Mesmo número, tipo e jurisdição, mas vindo de fontes diferentes (ex: Planalto vs Diário Oficial)
            return IdentityMatchStatus.POSSIBLE_MATCH

        return IdentityMatchStatus.NO_MATCH
