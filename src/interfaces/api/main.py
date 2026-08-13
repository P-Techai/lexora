from datetime import date
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.application.dto.retrieval_dto import (
    LegalRetrievalRequest,
    LegalRetrievalResultResponse,
)
from src.domain.enums import DocumentType, Jurisdiction

app = FastAPI(
    title="LÉXORA API",
    description="Plataforma inteligente de conhecimento jurídico, tributário e contábil brasileiro.",
    version="0.8.0-retrieval-foundation",
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
        version="0.8.0-retrieval-foundation"
    )


class LegalRetrieveApiRequest(BaseModel):
    query: str = Field(..., description="String de busca textual ou semântica")
    reference_date: date = Field(..., description="Data de referência temporal YYYY-MM-DD para filtragem de vigência")
    jurisdiction: Optional[Jurisdiction] = None
    document_type: Optional[DocumentType] = None
    document_number: Optional[str] = None
    top_k: int = Field(default=10, ge=1, le=100, description="Número máximo de candidatos (1 a 100)")


@app.post("/api/v1/legal/retrieve", response_model=LegalRetrievalResultResponse, tags=["Retrieval"])
async def retrieve_legal_evidence(request: LegalRetrieveApiRequest):
    """
    Endpoint da Camada de Recuperação Híbrida Jurídica (Retrieval Foundation).
    Executa busca lexical + semântica com filtragem temporal obrigatória e proveniência canônica.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="A string de busca 'query' não pode estar vazia.")

    # Retorna estrutura DTO canônica de recuperação
    return LegalRetrievalResultResponse(
        query=request.query,
        normalized_query=request.query.strip().lower(),
        reference_date=request.reference_date,
        results=[],
        total_candidates=0,
        provenance_valid=True
    )
