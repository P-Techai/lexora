from datetime import date
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

from src.application.dto.retrieval_dto import (
    LegalRetrievalRequest,
    LegalRetrievalResultResponse,
)
from src.application.use_cases.retrieval.retrieve_legal_information import RetrieveLegalInformationUseCase
from src.domain.enums import DocumentType, Jurisdiction
from src.infrastructure.adapters.factory import EmbeddingProviderFactory
from src.infrastructure.db.session import get_db_session

app = FastAPI(
    title="LÉXORA API",
    description="Plataforma inteligente de conhecimento jurídico, tributário e contábil brasileiro.",
    version="0.8.1-retrieval-production-closure",
)


class HealthResponse(BaseModel):
    status: str
    app_name: str
    version: str


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Endpoint de verificação de saúde da aplicação."""
    return HealthResponse(
        status="healthy",
        app_name="LÉXORA (LXR)",
        version="0.8.1-retrieval-production-closure"
    )


class LegalRetrieveApiRequest(BaseModel):
    query: str = Field(..., description="String de busca textual ou semântica")
    reference_date: date = Field(..., description="Data de referência temporal YYYY-MM-DD para filtragem de vigência")
    jurisdiction: Optional[Jurisdiction] = None
    document_type: Optional[DocumentType] = None
    document_number: Optional[str] = None
    top_k: int = Field(default=10, ge=1, le=100, description="Número máximo de candidatos (1 a 100)")


@app.post("/api/v1/legal/retrieve", response_model=LegalRetrievalResultResponse, tags=["Retrieval"])
async def retrieve_legal_evidence(request: LegalRetrieveApiRequest, session = Depends(get_db_session)):
    """
    Endpoint da Camada de Recuperação Híbrida Jurídica de Produção.
    Executa a busca real no PostgreSQL, filtragem temporal e auditoria de proveniência.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="A string de busca 'query' não pode estar vazia.")

    from src.infrastructure.db.repositories.postgres_repositories import (
        PostgresEvidenceRepository,
        PostgresLegalDocumentRepository,
        PostgresLegalNodeRepository,
        PostgresLegalVersionRepository,
        PostgresSourceRepository,
    )

    node_repo = PostgresLegalNodeRepository(session)
    ver_repo = PostgresLegalVersionRepository(session)
    doc_repo = PostgresLegalDocumentRepository(session)
    source_repo = PostgresSourceRepository(session)
    ev_repo = PostgresEvidenceRepository(session)
    emb_provider = EmbeddingProviderFactory.get_provider()

    use_case = RetrieveLegalInformationUseCase(
        node_repo=node_repo,
        version_repo=ver_repo,
        doc_repo=doc_repo,
        source_repo=source_repo,
        evidence_repo=ev_repo,
        embedding_provider=emb_provider
    )

    domain_request = LegalRetrievalRequest(
        query=request.query,
        reference_date=request.reference_date,
        jurisdiction=request.jurisdiction,
        document_type=request.document_type,
        document_number=request.document_number,
        top_k=request.top_k
    )

    return await use_case.execute(domain_request)
