import uuid
from typing import Tuple

from src.application.ports.repositories import LegalDocumentRepository, SourceRepository
from src.domain.entities.legal_document import LegalDocument
from src.domain.enums import DocumentType, Jurisdiction
from src.domain.exceptions import InvalidLegalDocumentError


class CreateDocumentUseCase:
    """Caso de uso para criar ou localizar uma unidade documental LegalDocument."""

    def __init__(self, doc_repo: LegalDocumentRepository, source_repo: SourceRepository):
        self.doc_repo = doc_repo
        self.source_repo = source_repo

    async def execute(
        self,
        source_id: str,
        document_type: DocumentType,
        document_number: str,
        title: str,
        ementa: str,
        jurisdiction: Jurisdiction,
        issuing_body: str,
        publication_date,
        official_url: str,
        document_hash: str
    ) -> Tuple[LegalDocument, bool]:
        """Retorna tupla (LegalDocument, created_flag)."""
        source = await self.source_repo.get_by_id(source_id)
        if not source:
            raise InvalidLegalDocumentError(f"Source com ID '{source_id}' não existe no repositório.")

        existing = await self.doc_repo.find_by_number_and_type(
            document_number=document_number,
            document_type=document_type,
            jurisdiction=jurisdiction
        )

        for doc in existing:
            if doc.source_id == source_id:
                return doc, False

        doc = LegalDocument(
            id=str(uuid.uuid4()),
            source_id=source_id,
            document_type=document_type,
            document_number=document_number,
            title=title,
            ementa=ementa,
            jurisdiction=jurisdiction,
            issuing_body=issuing_body,
            publication_date=publication_date,
            official_url=official_url,
            document_hash=document_hash
        )

        saved = await self.doc_repo.save(doc)
        return saved, True
