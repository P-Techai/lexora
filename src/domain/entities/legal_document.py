from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

from src.domain.enums import DocumentType, Jurisdiction


class LegalDocument(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    source_id: str
    document_type: DocumentType
    document_number: str
    title: str
    ementa: Optional[str] = None
    jurisdiction: Jurisdiction = Jurisdiction.FEDERAL
    issuing_body: str
    publication_date: Optional[date] = None
    official_url: Optional[str] = None
    document_hash: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
