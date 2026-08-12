from datetime import date, datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from src.domain.enums import DocumentType, Jurisdiction


class IngestionStatus(str, Enum):
    CREATED = "CREATED"
    DUPLICATE = "DUPLICATE"
    REJECTED = "REJECTED"
    UPDATED = "UPDATED"
    PENDING_REVIEW = "PENDING_REVIEW"


class LegalDocumentIngestionRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    source_id: str
    external_reference: Optional[str] = None
    document_type: DocumentType
    document_number: str
    title: str
    ementa: Optional[str] = None
    jurisdiction: Jurisdiction = Jurisdiction.FEDERAL
    issuing_body: str
    publication_date: Optional[date] = None
    official_url: Optional[str] = None
    raw_content: str
    content_type: str = "text/plain"
    captured_at: datetime = Field(default_factory=datetime.utcnow)


class LegalDocumentIngestionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    status: IngestionStatus
    document_id: Optional[str] = None
    version_id: Optional[str] = None
    content_hash: str
    created: bool = False
    duplicate: bool = False
    validation_errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
