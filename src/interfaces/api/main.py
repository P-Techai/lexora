import uuid
from datetime import date
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

from src.application.dto.fiscal_dto import (
    FiscalCalculateResponse,
    FiscalClassifyResponse,
    FiscalDecisionResponse,
    FiscalFactApiRequest,
    NFeImportRequest,
    NFeImportResponse,
)
from src.application.dto.retrieval_dto import (
    LegalRetrievalRequest,
    LegalRetrievalResultResponse,
)
from src.application.services.context_builder import LegalContextBuilder
from src.application.use_cases.retrieval.retrieve_and_answer import RetrieveAndAnswerUseCase
from src.application.use_cases.retrieval.retrieve_legal_information import RetrieveLegalInformationUseCase
from src.domain.decision.decision import Decision
from src.domain.entities.legal_answer import LegalAnswer
from src.domain.enums import DocumentType, Jurisdiction
from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.services.decision.decision_engine import DecisionEngine
from src.domain.services.fiscal.fiscal_classifier import FiscalClassifier
from src.domain.services.fiscal.tax_calculator import TaxCalculator
from src.domain.services.fiscal.tax_rule_evaluator import TaxRuleEvaluator
from src.infrastructure.adapters.factory import EmbeddingProviderFactory, LegalAnswerGeneratorFactory
from src.infrastructure.adapters.secure_nfe_parser import SecureNFeParser
from src.infrastructure.db.repositories.postgres_fiscal_repositories import PostgresFiscalTaxRuleRepository
from src.infrastructure.db.session import get_db_session

app = FastAPI(
    title="LÉXORA API",
    description="Plataforma inteligente de conhecimento jurídico, tributário e contábil brasileiro.",
    version="0.10.0-fiscal-brain-foundation",
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
        version="0.10.0-fiscal-brain-foundation"
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


# --- Endpoints da FASE 6.3 FISCAL BRAIN & DECISION ENGINE ---

@app.post("/api/v1/fiscal/classify", response_model=FiscalClassifyResponse, tags=["Fiscal Brain"])
async def classify_fiscal_fact(request: FiscalFactApiRequest):
    """
    Endpoint de classificação fiscal determinística de produto e fatos fiscais.
    """
    fact = FiscalFact(
        fact_id=f"fact_{uuid.uuid4().hex[:8]}",
        company_id=request.company_id,
        tax_regime=request.tax_regime,
        state=request.state,
        municipality=request.municipality,
        operation_type=request.operation_type,
        operation_date=request.operation_date,
        product_description=request.product_description,
        quantity=request.quantity,
        unit_value=request.unit_value,
        total_value=request.total_value,
        ncm=request.ncm,
        cest=request.cest,
        cfop=request.cfop,
        cst=request.cst,
        origin=request.origin,
        customer_type=request.customer_type,
        destination_state=request.destination_state,
        supplier_state=request.supplier_state,
        invoice_purpose=request.invoice_purpose,
        additional_fields=request.additional_fields
    )

    classification = FiscalClassifier.classify_fact(fact)
    return FiscalClassifyResponse(
        classification=classification,
        normalized_ncm=classification.ncm,
        normalized_cst=classification.cst,
        normalized_cfop=classification.cfop
    )


@app.post("/api/v1/fiscal/calculate", response_model=FiscalCalculateResponse, tags=["Fiscal Brain"])
async def calculate_fiscal_taxes(request: FiscalFactApiRequest, session = Depends(get_db_session)):
    """
    Endpoint de cálculo determinístico de tributos com base nas regras ativas na data de operação.
    """
    fact = FiscalFact(
        fact_id=f"fact_{uuid.uuid4().hex[:8]}",
        company_id=request.company_id,
        tax_regime=request.tax_regime,
        state=request.state,
        municipality=request.municipality,
        operation_type=request.operation_type,
        operation_date=request.operation_date,
        product_description=request.product_description,
        quantity=request.quantity,
        unit_value=request.unit_value,
        total_value=request.total_value,
        ncm=request.ncm,
        cest=request.cest,
        cfop=request.cfop,
        cst=request.cst,
        origin=request.origin,
        customer_type=request.customer_type,
        destination_state=request.destination_state,
        supplier_state=request.supplier_state,
        invoice_purpose=request.invoice_purpose,
        additional_fields=request.additional_fields
    )

    rule_repo = PostgresFiscalTaxRuleRepository(session)
    active_rules = await rule_repo.list_all_active_rules(request.operation_date)
    matching_rules = TaxRuleEvaluator.find_matching_rules(fact, active_rules)

    calculations = [TaxCalculator.calculate_tax(fact, r) for r in matching_rules]
    total_tax = sum((c.calculated_amount for c in calculations), start=request.total_value.__class__("0.00"))

    return FiscalCalculateResponse(
        calculations=calculations,
        total_tax_amount=total_tax,
        reference_date=request.operation_date
    )


@app.post("/api/v1/fiscal/decide", response_model=FiscalDecisionResponse, tags=["Decision Engine"])
@app.post("/api/v1/fiscal/evaluate", response_model=FiscalDecisionResponse, tags=["Decision Engine"])
async def decide_fiscal_operation(request: FiscalFactApiRequest, session = Depends(get_db_session)):
    """
    Endpoint do Decision Engine de Produção.
    Orquestra o Two-Brain Flow (Legal Brain + Fiscal Brain) produzindo decisão determinística com audit trail.
    """
    fact = FiscalFact(
        fact_id=f"fact_{uuid.uuid4().hex[:8]}",
        company_id=request.company_id,
        tax_regime=request.tax_regime,
        state=request.state,
        municipality=request.municipality,
        operation_type=request.operation_type,
        operation_date=request.operation_date,
        product_description=request.product_description,
        quantity=request.quantity,
        unit_value=request.unit_value,
        total_value=request.total_value,
        ncm=request.ncm,
        cest=request.cest,
        cfop=request.cfop,
        cst=request.cst,
        origin=request.origin,
        customer_type=request.customer_type,
        destination_state=request.destination_state,
        supplier_state=request.supplier_state,
        invoice_purpose=request.invoice_purpose,
        additional_fields=request.additional_fields
    )

    rule_repo = PostgresFiscalTaxRuleRepository(session)
    active_rules = await rule_repo.list_all_active_rules(request.operation_date)

    engine = DecisionEngine(available_rules=active_rules)
    decision: Decision = engine.evaluate(fact)

    return FiscalDecisionResponse(
        decision_id=decision.decision_id,
        status=decision.status,
        classification=decision.classification,
        tax_results=decision.tax_results,
        legal_basis=decision.legal_basis,
        warnings=decision.warnings,
        conflicts=decision.conflicts,
        review_required=decision.review_required,
        decision_hash=decision.decision_hash,
        reference_date=decision.reference_date
    )


@app.get("/api/v1/fiscal/decisions/{decision_id}", response_model=FiscalDecisionResponse, tags=["Decision Engine"])
@app.get("/api/v1/fiscal/decision/{decision_id}", response_model=FiscalDecisionResponse, tags=["Decision Engine"])
async def get_fiscal_decision_by_id(decision_id: str, session = Depends(get_db_session)):
    """
    Endpoint para recuperação de decisão fiscal histórica por ID determinístico.
    """
    from sqlalchemy import select
    from src.infrastructure.db.models.postgres_fiscal_models import FiscalDecisionModel

    stmt = select(FiscalDecisionModel).where(FiscalDecisionModel.decision_id == decision_id)
    result = await session.execute(stmt)
    m = result.scalar_one_or_none()

    if not m:
        raise HTTPException(status_code=404, detail=f"Decisão fiscal '{decision_id}' não encontrada.")

    return FiscalDecisionResponse(
        decision_id=m.decision_id,
        status=m.status,
        classification=m.classification,
        tax_results=m.tax_results,
        legal_basis=m.legal_basis,
        warnings=m.warnings or [],
        conflicts=m.conflicts or [],
        review_required=m.review_required,
        decision_hash=m.decision_hash,
        reference_date=m.reference_date
    )


@app.post("/api/v1/nfe/import", response_model=NFeImportResponse, tags=["NFe Import"])
async def import_nfe_xml(request: NFeImportRequest):
    """
    Endpoint de importação e parsing seguro de XML de NFe com verificação de idempotência SHA-256.
    """
    parser = SecureNFeParser()
    xml_bytes = request.xml_content.encode("utf-8")
    doc = parser.parse_xml(xml_bytes)

    return NFeImportResponse(
        access_key=doc.access_key,
        raw_xml_hash=doc.raw_xml_hash,
        issuer_cnpj=doc.issuer_cnpj,
        recipient_cnpj=doc.recipient_cnpj,
        issue_date=doc.issue_date,
        items_count=len(doc.items),
        total_invoice_amount=doc.total_invoice_amount
    )
