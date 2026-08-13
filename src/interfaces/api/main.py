from datetime import date
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

from src.application.dto.retrieval_dto import (
    LegalRetrievalRequest,
    LegalRetrievalResultResponse,
)
from src.application.services.context_builder import LegalContextBuilder
from src.application.use_cases.retrieval.retrieve_and_answer import RetrieveAndAnswerUseCase
from src.application.use_cases.retrieval.retrieve_legal_information import RetrieveLegalInformationUseCase
from src.domain.entities.legal_answer import LegalAnswer
from src.domain.enums import DocumentType, Jurisdiction
from src.infrastructure.adapters.factory import EmbeddingProviderFactory, LegalAnswerGeneratorFactory
from src.infrastructure.db.session import get_db_session

app = FastAPI(
    title="LÉXORA API",
    description="Plataforma inteligente de conhecimento jurídico, tributário e contábil brasileiro.",
    version="0.9.1-contextual-rag-production-lock",
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
        version="0.9.1-contextual-rag-production-lock"
    )


class LegalRetrieveApiRequest(BaseModel):
    query: str = Field(..., description="String de busca textual ou semântica")
    reference_date: date = Field(..., description="Data de referência temporal YYYY-MM-DD para filtragem de vigência")
    jurisdiction: Optional[Jurisdiction] = None
    document_type: Optional[DocumentType] = None
    document_number: Optional[str] = None
    top_k: int = Field(default=10, ge=1, le=100, description="Número máximo de candidatos (1 a 100)")


class LegalAnswerApiRequest(BaseModel):
    query: str = Field(..., description="Pergunta ou consulta jurídica do usuário")
    reference_date: date = Field(..., description="Data de referência temporal YYYY-MM-DD para avaliação de vigência")
    jurisdiction: Optional[Jurisdiction] = None
    document_type: Optional[DocumentType] = None
    document_number: Optional[str] = None
    top_k: int = Field(default=10, ge=1, le=100, description="Número máximo de candidatos a considerar (1 a 100)")


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


@app.post("/api/v1/legal/answer", response_model=LegalAnswer, tags=["Legal RAG"])
async def answer_legal_query(request: LegalAnswerApiRequest, session = Depends(get_db_session)):
    """
    Endpoint de Resposta Jurídica RAG Contextual de Produção.
    Instancia o gerador via LegalAnswerGeneratorFactory protegendo contra fallbacks de produção.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="A pergunta 'query' não pode estar vazia.")

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

    retrieval_use_case = RetrieveLegalInformationUseCase(
        node_repo=node_repo,
        version_repo=ver_repo,
        doc_repo=doc_repo,
        source_repo=source_repo,
        evidence_repo=ev_repo,
        embedding_provider=emb_provider
    )

    context_builder = LegalContextBuilder(max_nodes=request.top_k)
    answer_generator = LegalAnswerGeneratorFactory.get_generator()

    rag_use_case = RetrieveAndAnswerUseCase(
        retrieval_use_case=retrieval_use_case,
        context_builder=context_builder,
        answer_generator=answer_generator
    )

    return await rag_use_case.execute(
        query=request.query,
        reference_date=request.reference_date,
        jurisdiction=request.jurisdiction,
        document_type=request.document_type,
        document_number=request.document_number,
        top_k=request.top_k
    )
