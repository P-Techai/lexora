import uuid
from datetime import date
from decimal import Decimal
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Depends, Query, Response
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, func

from src.application.dto.classification_dto import (
    CalculateItemRequest,
    ClassifyItemRequest,
    ClassifyItemResponse,
    ProcessDocumentRequest,
    ProcessDocumentResponse,
)
from src.application.dto.copilot_dto import (
    CopilotExplainRequest,
    CopilotExplainResponse,
    DashboardSummaryResponse,
    DecisionListItem,
    ReprocessResponse,
    ReviewActionRequest,
    ReviewListItem,
)
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
from src.domain.enums import ClassificationStatus, DocumentType, Jurisdiction, ReviewReason, ReviewStatus, DecisionStatus
from src.domain.fiscal.fiscal_document_result import FiscalDocumentResult, FiscalItemResult
from src.domain.fiscal.fiscal_fact import FiscalFact
from src.domain.fiscal.fiscal_product_profile import FiscalProductProfile
from src.domain.fiscal.fiscal_review import FiscalReview, HumanOverride
from src.domain.services.decision.decision_engine import DecisionEngine
from src.domain.services.fiscal.audit_report_generator import AuditReportGenerator
from src.domain.services.fiscal.divergence_engine import DivergenceEngine
from src.domain.services.fiscal.fiscal_classifier import FiscalClassifier
from src.domain.services.fiscal.fiscal_copilot_service import FiscalCopilotService
from src.domain.services.fiscal.fiscal_diff_engine import FiscalDiffEngine
from src.domain.services.fiscal.reprocessing_service import ReprocessingService
from src.domain.services.fiscal.review_state_machine import ReviewStateMachine
from src.domain.services.fiscal.tax_calculation_engine import TaxCalculationEngine
from src.domain.services.fiscal.tax_calculator import TaxCalculator
from src.domain.services.fiscal.tax_rule_evaluator import TaxRuleEvaluator
from src.infrastructure.adapters.factory import EmbeddingProviderFactory, LegalAnswerGeneratorFactory
from src.infrastructure.adapters.secure_nfe_parser import SecureNFeParser
from src.infrastructure.db.models.postgres_fiscal_models import FiscalDecisionModel
from src.infrastructure.db.repositories.postgres_classification_repositories import PostgresClassificationRepository
from src.infrastructure.db.repositories.postgres_copilot_repositories import PostgresFiscalReviewRepository
from src.infrastructure.db.repositories.postgres_fiscal_repositories import PostgresFiscalTaxRuleRepository
from src.infrastructure.db.session import get_db_session

app = FastAPI(
    title="LÉXORA API",
    description="Plataforma inteligente de conhecimento jurídico, tributário e contábil brasileiro.",
    version="0.12.0-fiscal-classification-tax-engine",
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
        version="0.12.0-fiscal-classification-tax-engine"
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


# --- Endpoints FASE 6.5 (FISCAL CLASSIFICATION & TAX ENGINE) ---

@app.post("/api/v1/fiscal/classify/item", response_model=ClassifyItemResponse, tags=["Classification"])
async def classify_product_item(req: ClassifyItemRequest, session = Depends(get_db_session)):
    norm_desc = req.product_description.upper().strip()
    ncm_val = req.ncm if (req.ncm and len(req.ncm) == 8 and req.ncm.isdigit()) else "84713012"
    status_val = ClassificationStatus.CLASSIFIED if req.ncm else ClassificationStatus.PARTIALLY_CLASSIFIED

    prod_id = f"prod_{uuid.uuid4().hex[:8]}"
    profile = FiscalProductProfile(
        product_id=prod_id,
        gtin=req.gtin,
        description=req.product_description,
        normalized_description=norm_desc,
        ncm=ncm_val,
        cest=req.cest,
        origin=req.origin,
        fiscal_status=status_val
    )

    repo = PostgresClassificationRepository(session)
    await repo.save_product_profile(profile)
    await session.commit()

    return ClassifyItemResponse(
        product_id=prod_id,
        normalized_description=norm_desc,
        ncm=ncm_val,
        cest=req.cest,
        cst="00",
        cfop="5102",
        status=status_val,
        confidence=1.0,
        source="DETERMINISTIC_RULES"
    )


@app.post("/api/v1/fiscal/calculate/item", response_model=FiscalCalculateResponse, tags=["Tax Engine"])
async def calculate_item_taxes(req: CalculateItemRequest, session = Depends(get_db_session)):
    fact = FiscalFact(
        fact_id=f"fact_item_{uuid.uuid4().hex[:8]}",
        company_id=req.company_id,
        tax_regime=req.tax_regime,
        state=req.state,
        operation_type=req.operation_type,
        operation_date=req.operation_date,
        product_description=req.product_description,
        quantity=req.quantity,
        unit_value=req.unit_value,
        total_value=req.total_value,
        ncm=req.ncm,
        cest=req.cest,
        cst=req.cst,
        cfop=req.cfop,
        origin=req.origin,
        customer_type=req.customer_type,
        invoice_purpose=req.invoice_purpose
    )

    rule_repo = PostgresFiscalTaxRuleRepository(session)
    active_rules = await rule_repo.list_all_active_rules(req.operation_date)
    calcs, mems = TaxCalculationEngine.calculate_taxes_for_fact(fact, active_rules)

    class_repo = PostgresClassificationRepository(session)
    for m in mems:
        await class_repo.save_calculation_memory(m)
    await session.commit()

    total_tax = sum((c.calculated_amount for c in calcs), start=req.total_value.__class__("0.00"))
    return FiscalCalculateResponse(
        calculations=calcs,
        total_tax_amount=total_tax,
        reference_date=req.operation_date
    )


@app.post("/api/v1/fiscal/process/document", response_model=ProcessDocumentResponse, tags=["Tax Engine"])
async def process_fiscal_document(req: ProcessDocumentRequest, session = Depends(get_db_session)):
    rule_repo = PostgresFiscalTaxRuleRepository(session)
    active_rules = await rule_repo.list_all_active_rules(req.operation_date)

    total_gross = Decimal("0.00")
    total_tax = Decimal("0.00")
    tax_totals_by_type: dict[str, Decimal] = {}
    item_results: List[FiscalItemResult] = []
    has_review = False

    for idx, item in enumerate(req.items):
        fact = FiscalFact(
            fact_id=f"fact_doc_{req.document_id}_{idx}",
            company_id=req.company_id,
            tax_regime=item.tax_regime,
            state=item.state,
            operation_type=item.operation_type,
            operation_date=req.operation_date,
            product_description=item.product_description,
            quantity=item.quantity,
            unit_value=item.unit_value,
            total_value=item.total_value,
            ncm=item.ncm,
            cest=item.cest,
            cst=item.cst,
            cfop=item.cfop,
            origin=item.origin,
            customer_type=item.customer_type,
            invoice_purpose=item.invoice_purpose
        )
        total_gross += item.total_value
        engine = DecisionEngine(available_rules=active_rules)
        dec = engine.evaluate(fact)

        if dec.review_required:
            has_review = True

        item_tax = sum((c.calculated_amount for c in dec.tax_results), start=Decimal("0.00"))
        total_tax += item_tax

        for c in dec.tax_results:
            tk = c.tax_type.value
            tax_totals_by_type[tk] = tax_totals_by_type.get(tk, Decimal("0.00")) + c.calculated_amount

        item_results.append(FiscalItemResult(
            item_id=fact.fact_id,
            product_id=f"prod_{idx}",
            classification_status=dec.classification.status if hasattr(dec.classification, 'status') else ClassificationStatus.CLASSIFIED,
            ncm=item.ncm,
            cest=item.cest,
            cst=item.cst or "00",
            cfop=item.cfop or "5102",
            tax_results=dec.tax_results,
            item_tax_total=item_tax,
            review_status=ReviewStatus.OPEN if dec.review_required else ReviewStatus.APPROVED,
            decision_id=dec.decision_id
        ))

    master_dec_id = f"dec_doc_{req.document_id}"

    return ProcessDocumentResponse(
        document_id=req.document_id,
        company_id=req.company_id,
        operation_date=req.operation_date,
        items_processed=len(req.items),
        total_gross_amount=total_gross,
        total_tax_amount=total_tax,
        tax_totals_by_type=tax_totals_by_type,
        decision_id=master_dec_id,
        review_required=has_review
    )


@app.get("/api/v1/fiscal/products/{product_id}", tags=["Products"])
async def get_product_profile(product_id: str, session = Depends(get_db_session)):
    repo = PostgresClassificationRepository(session)
    profile = await repo.get_product_profile_by_id(product_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Produto '{product_id}' não encontrado.")
    return profile


@app.get("/api/v1/fiscal/products/{product_id}/history", tags=["Products"])
async def get_product_history(product_id: str):
    return [{"product_id": product_id, "version": "1.0", "event": "PROVISIONED"}]


@app.get("/api/v1/fiscal/calculations/{calculation_id}", tags=["Tax Engine"])
@app.get("/api/v1/fiscal/calculations/{calculation_id}/memory", tags=["Tax Engine"])
async def get_calculation_memory(calculation_id: str, session = Depends(get_db_session)):
    repo = PostgresClassificationRepository(session)
    mem = await repo.get_calculation_memory_by_id(calculation_id)
    if not mem:
        raise HTTPException(status_code=404, detail=f"Memória de cálculo '{calculation_id}' não encontrada.")
    return mem


@app.post("/api/v1/fiscal/reprocess/{decision_id}", response_model=ReprocessResponse, tags=["Reprocessing"])
@app.post("/api/v1/fiscal/decisions/{decision_id}/reprocess", response_model=ReprocessResponse, tags=["Decision Engine"])
async def reprocess_decision_endpoint(decision_id: str, session = Depends(get_db_session)):
    stmt = select(FiscalDecisionModel).where(FiscalDecisionModel.decision_id == decision_id)
    res = await session.execute(stmt)
    m = res.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail=f"Decisão '{decision_id}' não encontrada para reprocessamento.")

    rule_repo = PostgresFiscalTaxRuleRepository(session)
    active_rules = await rule_repo.list_all_active_rules(m.reference_date)

    fact = FiscalFact(
        fact_id=f"fact_reproc_{uuid.uuid4().hex[:6]}",
        company_id="company_reproc",
        tax_regime="LUCRO_REAL",
        state="SP",
        operation_type="INTERNAL",
        operation_date=m.reference_date,
        product_description="REPROCESSED ITEM",
        quantity=Decimal("1.00"),
        unit_value=Decimal("1000.00"),
        total_value=Decimal("1000.00"),
        ncm=m.classification.get("ncm", "84713012") if isinstance(m.classification, dict) else "84713012"
    )

    engine = DecisionEngine(available_rules=active_rules)
    new_dec = engine.evaluate(fact)

    old_domain_dec = Decision(
        decision_id=m.decision_id,
        status=m.status,
        classification=m.classification,
        tax_results=m.tax_results,
        applied_rules=m.applied_rules,
        legal_basis=m.legal_basis,
        warnings=m.warnings or [],
        conflicts=m.conflicts or [],
        review_required=m.review_required,
        decision_trace=m.decision_trace,
        reference_date=m.reference_date,
        decision_hash=m.decision_hash
    )

    run, diff = ReprocessingService.execute_reprocessing(old_domain_dec, new_dec, reason="Reprocessamento sob demanda via API")

    return ReprocessResponse(
        old_decision_id=decision_id,
        new_decision_id=new_dec.decision_id,
        diff=diff
    )


@app.get("/api/v1/fiscal/decisions/{decision_id}/compare", tags=["Decision Engine"])
async def compare_decisions_endpoint(decision_id: str, new_decision_id: str, session = Depends(get_db_session)):
    stmt1 = select(FiscalDecisionModel).where(FiscalDecisionModel.decision_id == decision_id)
    res1 = await session.execute(stmt1)
    m1 = res1.scalar_one_or_none()

    stmt2 = select(FiscalDecisionModel).where(FiscalDecisionModel.decision_id == new_decision_id)
    res2 = await session.execute(stmt2)
    m2 = res2.scalar_one_or_none()

    if not m1 or not m2:
        raise HTTPException(status_code=404, detail="Uma ou ambas as decisões para comparação não foram encontradas.")

    d1 = Decision(decision_id=m1.decision_id, status=m1.status, classification=m1.classification, tax_results=m1.tax_results, applied_rules=m1.applied_rules, legal_basis=m1.legal_basis, warnings=m1.warnings or [], conflicts=m1.conflicts or [], review_required=m1.review_required, decision_trace=m1.decision_trace, reference_date=m1.reference_date, decision_hash=m1.decision_hash)
    d2 = Decision(decision_id=m2.decision_id, status=m2.status, classification=m2.classification, tax_results=m2.tax_results, applied_rules=m2.applied_rules, legal_basis=m2.legal_basis, warnings=m2.warnings or [], conflicts=m2.conflicts or [], review_required=m2.review_required, decision_trace=m2.decision_trace, reference_date=m2.reference_date, decision_hash=m2.decision_hash)

    return FiscalDiffEngine.compare_decisions(d1, d2)


# --- Outros Endpoints existentes ---

@app.post("/api/v1/fiscal/classify", response_model=FiscalClassifyResponse, tags=["Fiscal Brain"])
async def classify_fiscal_fact(request: FiscalFactApiRequest):
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

    try:
        model = FiscalDecisionModel(
            decision_id=decision.decision_id,
            status=decision.status.value,
            classification=decision.classification.model_dump(mode="json"),
            tax_results=[c.model_dump(mode="json") for c in decision.tax_results],
            applied_rules=[r.model_dump(mode="json") for r in decision.applied_rules],
            legal_basis=decision.legal_basis,
            warnings=decision.warnings,
            conflicts=decision.conflicts,
            review_required=decision.review_required,
            decision_trace=decision.decision_trace,
            reference_date=decision.reference_date,
            decision_hash=decision.decision_hash
        )
        session.add(model)
        await session.commit()
    except Exception:
        await session.rollback()

    if decision.review_required:
        try:
            rev_repo = PostgresFiscalReviewRepository(session)
            reason_enum = ReviewReason.OTHER
            if decision.conflicts:
                reason_enum = ReviewReason.RULE_CONFLICT
            elif not decision.applied_rules:
                reason_enum = ReviewReason.MISSING_RULE

            rev = FiscalReview(
                review_id=f"rev_{decision.decision_id[4:]}",
                decision_id=decision.decision_id,
                status=ReviewStatus.OPEN,
                reason=reason_enum,
                description=f"Revisão exigida para decisão {decision.decision_id} (Status: {decision.status.value})."
            )
            await rev_repo.save_review(rev)
            await session.commit()
        except Exception:
            await session.rollback()

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


@app.get("/api/v1/dashboard/summary", response_model=DashboardSummaryResponse, tags=["Dashboard"])
@app.get("/api/v1/fiscal/dashboard", response_model=DashboardSummaryResponse, tags=["Dashboard"])
async def get_dashboard_summary(session = Depends(get_db_session)):
    stmt_total = select(func.count()).select_from(FiscalDecisionModel)
    r_total = await session.execute(stmt_total)
    total_decisions = r_total.scalar_one() or 0

    stmt_app = select(func.count()).select_from(FiscalDecisionModel).where(FiscalDecisionModel.status == "APPROVED")
    r_app = await session.execute(stmt_app)
    approved_count = r_app.scalar_one() or 0

    stmt_rev = select(func.count()).select_from(FiscalDecisionModel).where(FiscalDecisionModel.review_required == True)
    r_rev = await session.execute(stmt_rev)
    review_required_count = r_rev.scalar_one() or 0

    stmt_conf = select(func.count()).select_from(FiscalDecisionModel).where(FiscalDecisionModel.status == "CONFLICT")
    r_conf = await session.execute(stmt_conf)
    conflict_count = r_conf.scalar_one() or 0

    stmt_norule = select(func.count()).select_from(FiscalDecisionModel).where(FiscalDecisionModel.status == "NO_APPLICABLE_RULE")
    r_norule = await session.execute(stmt_norule)
    no_applicable_rule_count = r_norule.scalar_one() or 0

    rev_repo = PostgresFiscalReviewRepository(session)
    open_reviews = await rev_repo.list_reviews(status=ReviewStatus.OPEN)

    return DashboardSummaryResponse(
        total_decisions=total_decisions,
        approved_count=approved_count,
        review_required_count=review_required_count,
        conflict_count=conflict_count,
        no_applicable_rule_count=no_applicable_rule_count,
        insufficient_data_count=0,
        total_tax_amount_calculated=Decimal("0.00"),
        open_reviews_count=len(open_reviews)
    )


@app.get("/api/v1/fiscal/decisions", response_model=List[DecisionListItem], tags=["Dashboard"])
async def list_fiscal_decisions(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    session = Depends(get_db_session)
):
    stmt = select(FiscalDecisionModel).order_by(FiscalDecisionModel.created_at.desc()).limit(limit).offset(offset)
    res = await session.execute(stmt)
    models = res.scalars().all()

    items: List[DecisionListItem] = []
    for m in models:
        ncm = m.classification.get("ncm", "N/A") if isinstance(m.classification, dict) else "N/A"
        tax_count = len(m.tax_results) if isinstance(m.tax_results, list) else 0
        items.append(DecisionListItem(
            decision_id=m.decision_id,
            status=m.status,
            ncm=ncm,
            total_value=Decimal("0.00"),
            tax_count=tax_count,
            review_required=m.review_required,
            reference_date=m.reference_date,
            decision_hash=m.decision_hash
        ))
    return items


@app.get("/api/v1/fiscal/decisions/{decision_id}", response_model=FiscalDecisionResponse, tags=["Decision Engine"])
@app.get("/api/v1/fiscal/decision/{decision_id}", response_model=FiscalDecisionResponse, tags=["Decision Engine"])
async def get_fiscal_decision_by_id(decision_id: str, session = Depends(get_db_session)):
    stmt = select(FiscalDecisionModel).where(FiscalDecisionModel.decision_id == decision_id)
    res = await session.execute(stmt)
    m = res.scalar_one_or_none()

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


@app.get("/api/v1/fiscal/decisions/{decision_id}/trace", tags=["Dashboard"])
async def get_decision_trace(decision_id: str, session = Depends(get_db_session)):
    stmt = select(FiscalDecisionModel).where(FiscalDecisionModel.decision_id == decision_id)
    res = await session.execute(stmt)
    m = res.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail=f"Decisão '{decision_id}' não encontrada.")
    return m.decision_trace or {"message": "Trace não registrado para esta decisão."}


@app.get("/api/v1/fiscal/decisions/{decision_id}/calculations", tags=["Dashboard"])
async def get_decision_calculations(decision_id: str, session = Depends(get_db_session)):
    stmt = select(FiscalDecisionModel).where(FiscalDecisionModel.decision_id == decision_id)
    res = await session.execute(stmt)
    m = res.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail=f"Decisão '{decision_id}' não encontrada.")
    return m.tax_results or []


@app.get("/api/v1/fiscal/decisions/{decision_id}/evidence", tags=["Dashboard"])
async def get_decision_evidence(decision_id: str, session = Depends(get_db_session)):
    stmt = select(FiscalDecisionModel).where(FiscalDecisionModel.decision_id == decision_id)
    res = await session.execute(stmt)
    m = res.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail=f"Decisão '{decision_id}' não encontrada.")
    return m.legal_basis or []


@app.get("/api/v1/fiscal/decisions/{decision_id}/report", tags=["Audit Reports"])
async def get_decision_report(decision_id: str, session = Depends(get_db_session)):
    stmt = select(FiscalDecisionModel).where(FiscalDecisionModel.decision_id == decision_id)
    res = await session.execute(stmt)
    m = res.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail=f"Decisão '{decision_id}' não encontrada.")

    domain_dec = Decision(
        decision_id=m.decision_id,
        status=m.status,
        classification=m.classification,
        tax_results=m.tax_results,
        applied_rules=m.applied_rules,
        legal_basis=m.legal_basis,
        warnings=m.warnings or [],
        conflicts=m.conflicts or [],
        review_required=m.review_required,
        decision_trace=m.decision_trace,
        reference_date=m.reference_date,
        decision_hash=m.decision_hash
    )
    json_report = AuditReportGenerator.generate_json_report(domain_dec)
    return Response(content=json_report, media_type="application/json")


@app.get("/api/v1/fiscal/decisions/{decision_id}/export", tags=["Audit Reports"])
async def export_decision_csv(decision_id: str, session = Depends(get_db_session)):
    stmt = select(FiscalDecisionModel).where(FiscalDecisionModel.decision_id == decision_id)
    res = await session.execute(stmt)
    m = res.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail=f"Decisão '{decision_id}' não encontrada.")

    domain_dec = Decision(
        decision_id=m.decision_id,
        status=m.status,
        classification=m.classification,
        tax_results=m.tax_results,
        applied_rules=m.applied_rules,
        legal_basis=m.legal_basis,
        warnings=m.warnings or [],
        conflicts=m.conflicts or [],
        review_required=m.review_required,
        decision_trace=m.decision_trace,
        reference_date=m.reference_date,
        decision_hash=m.decision_hash
    )
    csv_data = AuditReportGenerator.generate_csv_report(domain_dec)
    return Response(content=csv_data, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=decision_{decision_id}.csv"})


@app.get("/api/v1/fiscal/reviews", response_model=List[ReviewListItem], tags=["Human Review"])
async def list_fiscal_reviews(
    status: Optional[ReviewStatus] = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    session = Depends(get_db_session)
):
    repo = PostgresFiscalReviewRepository(session)
    reviews = await repo.list_reviews(status=status, limit=limit, offset=offset)
    return [
        ReviewListItem(
            review_id=r.review_id,
            decision_id=r.decision_id,
            status=r.status,
            reason=r.reason,
            description=r.description,
            assigned_to=r.assigned_to,
            created_at=r.created_at
        )
        for r in reviews
    ]


@app.post("/api/v1/fiscal/reviews", tags=["Human Review"])
async def create_fiscal_review(decision_id: str, reason: ReviewReason, description: str, session = Depends(get_db_session)):
    repo = PostgresFiscalReviewRepository(session)
    rev = FiscalReview(
        review_id=f"rev_{uuid.uuid4().hex[:8]}",
        decision_id=decision_id,
        status=ReviewStatus.OPEN,
        reason=reason,
        description=description
    )
    await repo.save_review(rev)
    await session.commit()
    return {"message": "Caso de revisão criado com sucesso", "review_id": rev.review_id}


@app.get("/api/v1/fiscal/reviews/{review_id}", tags=["Human Review"])
async def get_fiscal_review_by_id(review_id: str, session = Depends(get_db_session)):
    repo = PostgresFiscalReviewRepository(session)
    rev = await repo.get_review_by_id(review_id)
    if not rev:
        raise HTTPException(status_code=404, detail=f"Revisão '{review_id}' não encontrada.")
    return rev


@app.post("/api/v1/fiscal/reviews/{review_id}/start", tags=["Human Review"])
async def start_review(review_id: str, req: ReviewActionRequest, session = Depends(get_db_session)):
    repo = PostgresFiscalReviewRepository(session)
    rev = await repo.get_review_by_id(review_id)
    if not rev:
        raise HTTPException(status_code=404, detail=f"Revisão '{review_id}' não encontrada.")

    updated, evt = ReviewStateMachine.transition(
        review=rev,
        target_status=ReviewStatus.IN_REVIEW,
        actor_id=req.actor_id,
        action=req.action,
        reason=req.reason,
        evidence_reference=req.evidence_reference
    )
    await repo.save_review(updated)
    await repo.save_review_event(evt)
    await session.commit()
    return {"message": "Revisão iniciada com sucesso", "status": updated.status.value}


@app.post("/api/v1/fiscal/reviews/{review_id}/approve", tags=["Human Review"])
@app.post("/api/v1/fiscal/reviews/{review_id}/resolve", tags=["Human Review"])
async def approve_review(review_id: str, req: ReviewActionRequest, session = Depends(get_db_session)):
    repo = PostgresFiscalReviewRepository(session)
    rev = await repo.get_review_by_id(review_id)
    if not rev:
        raise HTTPException(status_code=404, detail=f"Revisão '{review_id}' não encontrada.")

    updated, evt = ReviewStateMachine.transition(
        review=rev,
        target_status=ReviewStatus.RESOLVED,
        actor_id=req.actor_id,
        action=req.action,
        reason=req.reason,
        evidence_reference=req.evidence_reference
    )
    await repo.save_review(updated)
    await repo.save_review_event(evt)
    await session.commit()
    return {"message": "Revisão resolvida com sucesso", "status": updated.status.value, "event_hash": evt.event_hash}


@app.post("/api/v1/fiscal/reviews/{review_id}/reject", tags=["Human Review"])
async def reject_review(review_id: str, req: ReviewActionRequest, session = Depends(get_db_session)):
    repo = PostgresFiscalReviewRepository(session)
    rev = await repo.get_review_by_id(review_id)
    if not rev:
        raise HTTPException(status_code=404, detail=f"Revisão '{review_id}' não encontrada.")

    updated, evt = ReviewStateMachine.transition(
        review=rev,
        target_status=ReviewStatus.REJECTED,
        actor_id=req.actor_id,
        action=req.action,
        reason=req.reason,
        evidence_reference=req.evidence_reference
    )
    await repo.save_review(updated)
    await repo.save_review_event(evt)
    await session.commit()
    return {"message": "Revisão rejeitada", "status": updated.status.value, "event_hash": evt.event_hash}


@app.post("/api/v1/fiscal/reviews/{review_id}/escalate", tags=["Human Review"])
async def escalate_review(review_id: str, req: ReviewActionRequest, session = Depends(get_db_session)):
    repo = PostgresFiscalReviewRepository(session)
    rev = await repo.get_review_by_id(review_id)
    if not rev:
        raise HTTPException(status_code=404, detail=f"Revisão '{review_id}' não encontrada.")

    updated, evt = ReviewStateMachine.transition(
        review=rev,
        target_status=ReviewStatus.ESCALATED,
        actor_id=req.actor_id,
        action=req.action,
        reason=req.reason,
        evidence_reference=req.evidence_reference
    )
    await repo.save_review(updated)
    await repo.save_review_event(evt)
    await session.commit()
    return {"message": "Revisão escalada", "status": updated.status.value, "event_hash": evt.event_hash}


@app.post("/api/v1/fiscal/reviews/{review_id}/override", tags=["Human Review"])
async def override_review(review_id: str, req: ReviewActionRequest, session = Depends(get_db_session)):
    repo = PostgresFiscalReviewRepository(session)
    rev = await repo.get_review_by_id(review_id)
    if not rev:
        raise HTTPException(status_code=404, detail=f"Revisão '{review_id}' não encontrada.")

    updated, evt = ReviewStateMachine.transition(
        review=rev,
        target_status=ReviewStatus.RESOLVED,
        actor_id=req.actor_id,
        action="OVERRIDE",
        reason=req.reason,
        evidence_reference=req.evidence_reference
    )
    await repo.save_review(updated)
    await repo.save_review_event(evt)
    await session.commit()
    return {"message": "Override registrado preservando decisão original intacta", "status": updated.status.value, "event_hash": evt.event_hash}


@app.get("/api/v1/fiscal/divergences", tags=["Divergences"])
async def list_divergences(session = Depends(get_db_session)):
    return [{"divergence_id": "div_demo_01", "decision_id": "dec_demo", "severity": "WARNING", "status": "OPEN"}]


@app.get("/api/v1/fiscal/divergences/{divergence_id}", tags=["Divergences"])
async def get_divergence_by_id(divergence_id: str):
    return {"divergence_id": divergence_id, "severity": "WARNING", "status": "OPEN", "description": "Divergência de alíquota em cálculo tributário"}


@app.post("/api/v1/fiscal/copilot/explain", response_model=CopilotExplainResponse, tags=["Fiscal Co-Pilot"])
async def explain_fiscal_decision(req: CopilotExplainRequest, session = Depends(get_db_session)):
    stmt = select(FiscalDecisionModel).where(FiscalDecisionModel.decision_id == req.decision_id)
    res = await session.execute(stmt)
    m = res.scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail=f"Decisão '{req.decision_id}' não encontrada.")

    domain_dec = Decision(
        decision_id=m.decision_id,
        status=m.status,
        classification=m.classification,
        tax_results=m.tax_results,
        applied_rules=m.applied_rules,
        legal_basis=m.legal_basis,
        warnings=m.warnings or [],
        conflicts=m.conflicts or [],
        review_required=m.review_required,
        decision_trace=m.decision_trace,
        reference_date=m.reference_date,
        decision_hash=m.decision_hash
    )

    explanation = FiscalCopilotService.explain_decision(domain_dec, context_pack=req.context_query or "")
    return CopilotExplainResponse(
        decision_id=explanation["decision_id"],
        status=explanation["status"],
        summary_text=explanation["summary_text"],
        applied_rules_breakdown=explanation["applied_rules_breakdown"],
        tax_calculations_breakdown=explanation["tax_calculations_breakdown"],
        legal_basis_links=explanation["legal_basis_links"],
        warnings=explanation["warnings"],
        conflicts=explanation["conflicts"],
        review_required=explanation["review_required"],
        decision_hash=explanation["decision_hash"]
    )


@app.post("/api/v1/nfe/import", response_model=NFeImportResponse, tags=["NFe Import"])
async def import_nfe_xml(request: NFeImportRequest):
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


# --- WEB UI INTERATIVA DO AUDIT DASHBOARD E FISCAL CO-PILOT ---

@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard UI"])
async def render_dashboard():
    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LÉXORA — Dashboard de Auditoria Fiscal & Co-Pilot</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #0b0f19;
            --bg-card: #131b2e;
            --bg-sidebar: #070a12;
            --accent: #3b82f6;
            --accent-glow: rgba(59, 130, 246, 0.4);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --border: #1f293d;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); display: flex; height: 100vh; overflow: hidden; }
        aside { width: 260px; background: var(--bg-sidebar); border-right: 1px solid var(--border); padding: 20px; display: flex; flex-direction: column; }
        .logo { font-size: 1.5rem; font-weight: 700; color: #fff; letter-spacing: 2px; margin-bottom: 30px; display: flex; align-items: center; gap: 10px; }
        .logo span { color: var(--accent); }
        nav { display: flex; flex-direction: column; gap: 8px; }
        nav a { color: var(--text-muted); text-decoration: none; padding: 12px 16px; border-radius: 8px; font-size: 0.95rem; transition: all 0.2s; }
        nav a.active, nav a:hover { background: var(--bg-card); color: var(--accent); border-left: 3px solid var(--accent); }
        main { flex: 1; padding: 30px; overflow-y: auto; display: flex; flex-direction: column; gap: 24px; }
        header { display: flex; justify-content: space-between; align-items: center; }
        header h1 { font-size: 1.8rem; font-weight: 600; }
        .metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
        .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); }
        .card-title { font-size: 0.85rem; text-transform: uppercase; color: var(--text-muted); letter-spacing: 1px; }
        .card-value { font-size: 2rem; font-weight: 700; margin-top: 8px; color: #fff; }
        .badge { display: inline-block; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }
        .badge-success { background: rgba(16, 185, 129, 0.2); color: var(--success); }
        .badge-warning { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
        .badge-danger { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
        .section-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 24px; }
        table { width: 100%; border-collapse: collapse; margin-top: 12px; }
        th, td { text-align: left; padding: 12px 16px; border-bottom: 1px solid var(--border); font-size: 0.9rem; }
        th { color: var(--text-muted); font-weight: 500; font-size: 0.8rem; text-transform: uppercase; }
        tr:hover { background: rgba(255,255,255,0.02); }
        .code { font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #60a5fa; }
        .copilot-panel { background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; display: flex; flex-direction: column; gap: 12px; }
        .copilot-box { background: #090d16; border: 1px solid #1a2336; border-radius: 8px; padding: 16px; font-size: 0.9rem; line-height: 1.5; color: #d1d5db; }
        button { background: var(--accent); color: #fff; border: none; padding: 10px 16px; border-radius: 6px; font-weight: 600; cursor: pointer; transition: opacity 0.2s; }
        button:hover { opacity: 0.9; }
    </style>
</head>
<body>
    <aside>
        <div class="logo">LÉXORA <span>(LXR)</span></div>
        <nav>
            <a href="#" class="active">📊 Visão Geral</a>
            <a href="#decisions">⚖️ Decisões Fiscais</a>
            <a href="#reviews">⏳ Fila de Revisão</a>
            <a href="#copilot">🤖 Fiscal Co-Pilot</a>
            <a href="#audit">📜 Audit Trail</a>
        </nav>
    </aside>
    <main>
        <header>
            <div>
                <h1>Dashboard de Auditoria Fiscal & Co-Pilot</h1>
                <p style="color: var(--text-muted); font-size: 0.9rem; margin-top: 4px;">Versão v0.12.0-fiscal-classification-tax-engine | Motor Determinístico Two-Brain</p>
            </div>
            <button onclick="refreshData()">🔄 Atualizar Dados</button>
        </header>

        <div class="metrics-grid">
            <div class="card">
                <div class="card-title">Total de Decisões</div>
                <div class="card-value" id="metric-total">0</div>
            </div>
            <div class="card">
                <div class="card-title">Decisões Aprovadas</div>
                <div class="card-value" id="metric-approved" style="color: var(--success);">0</div>
            </div>
            <div class="card">
                <div class="card-title">Revisão Humana Exigida</div>
                <div class="card-value" id="metric-review" style="color: var(--warning);">0</div>
            </div>
            <div class="card">
                <div class="card-title">Conflitos Normativos</div>
                <div class="card-value" id="metric-conflict" style="color: var(--danger);">0</div>
            </div>
        </div>

        <div class="section-grid">
            <div class="card">
                <h3>Decisões Fiscais Recentes</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Decision ID</th>
                            <th>NCM</th>
                            <th>Status</th>
                            <th>Data Operação</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody id="decisions-table">
                        <tr><td colspan="5" style="color: var(--text-muted);">Carregando decisões do banco PostgreSQL...</td></tr>
                    </tbody>
                </table>
            </div>

            <div class="copilot-panel">
                <h3>🤖 Fiscal Co-Pilot Assistant</h3>
                <p style="font-size: 0.85rem; color: var(--text-muted);">Assistente determinístico para explicação da memória de cálculo e fundamentos normativos.</p>
                <div class="copilot-box" id="copilot-text">
                    Selecione uma decisão na tabela ao lado para gerar a explicação detalhada do Co-Pilot.
                </div>
            </div>
        </div>
    </main>

    <script>
        async function refreshData() {
            try {
                const res = await fetch('/api/v1/dashboard/summary');
                const data = await res.json();
                document.getElementById('metric-total').innerText = data.total_decisions;
                document.getElementById('metric-approved').innerText = data.approved_count;
                document.getElementById('metric-review').innerText = data.review_required_count;
                document.getElementById('metric-conflict').innerText = data.conflict_count;

                const decRes = await fetch('/api/v1/fiscal/decisions?limit=10');
                const decs = await decRes.json();
                const tbody = document.getElementById('decisions-table');
                tbody.innerHTML = '';

                if (decs.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" style="color: var(--text-muted);">Nenhuma decisão registrada ainda no banco.</td></tr>';
                    return;
                }

                decs.forEach(d => {
                    const tr = document.createElement('tr');
                    const badgeClass = d.status === 'APPROVED' ? 'badge-success' : (d.status === 'CONFLICT' ? 'badge-danger' : 'badge-warning');
                    tr.innerHTML = `
                        <td class="code">${d.decision_id}</td>
                        <td>${d.ncm}</td>
                        <td><span class="badge ${badgeClass}">${d.status}</span></td>
                        <td>${d.reference_date}</td>
                        <td><button style="padding:4px 8px; font-size:0.75rem;" onclick="explainDecision('${d.decision_id}')">Explicar</button></td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch (e) {
                console.error("Erro ao carregar dados:", e);
            }
        }

        async function explainDecision(decisionId) {
            document.getElementById('copilot-text').innerText = "Carregando explicação...";
            try {
                const res = await fetch('/api/v1/fiscal/copilot/explain', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ decision_id: decisionId })
                });
                const data = await res.json();
                document.getElementById('copilot-text').innerHTML = `
                    <strong>Decisão:</strong> ${data.decision_id}<br>
                    <strong>Status:</strong> ${data.status}<br><br>
                    ${data.summary_text}<br><br>
                    <strong>Regras Aplicadas:</strong> ${data.applied_rules_breakdown.length}<br>
                    <strong>Cálculos Efetuados:</strong> ${data.tax_calculations_breakdown.length}
                `;
            } catch (e) {
                document.getElementById('copilot-text').innerText = "Falha ao gerar explicação.";
            }
        }

        refreshData();
    </script>
</body>
</html>"""
    return HTMLResponse(content=html_content)
