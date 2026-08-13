from datetime import date
from typing import Optional

from src.application.dto.retrieval_dto import LegalRetrievalRequest
from src.application.ports.legal_answer_generator import LegalAnswerGenerator
from src.application.services.context_builder import LegalContextBuilder
from src.application.services.guardrails.answer_guard import LegalAnswerGuard
from src.application.use_cases.retrieval.retrieve_legal_information import RetrieveLegalInformationUseCase
from src.domain.entities.legal_answer import LegalAnswer
from src.domain.enums import DocumentType, Jurisdiction


class RetrieveAndAnswerUseCase:
    """
    Caso de Uso Completo do RAG Jurídico Contextual de Produção (11 Estágios):
    QUERY NORMALIZATION -> HYBRID RETRIEVAL -> TEMPORAL FILTER -> PROVENANCE VALIDATION -> CONFLICT DETECTION ->
    CONTEXT ASSEMBLY -> LLM GENERATION -> ANSWER VALIDATION -> CITATION VALIDATION -> FINAL LEGAL RESPONSE
    """

    def __init__(
        self,
        retrieval_use_case: RetrieveLegalInformationUseCase,
        context_builder: LegalContextBuilder,
        answer_generator: LegalAnswerGenerator
    ):
        self.retrieval_use_case = retrieval_use_case
        self.context_builder = context_builder
        self.answer_generator = answer_generator

    async def execute(
        self,
        query: str,
        reference_date: date,
        jurisdiction: Optional[Jurisdiction] = None,
        document_type: Optional[DocumentType] = None,
        document_number: Optional[str] = None,
        top_k: int = 10
    ) -> LegalAnswer:
        # 1. Executa Recuperação Híbrida com Filtragem Temporal e Proveniência (Estágios 1 a 5)
        retrieval_request = LegalRetrievalRequest(
            query=query,
            reference_date=reference_date,
            jurisdiction=jurisdiction,
            document_type=document_type,
            document_number=document_number,
            top_k=top_k
        )
        retrieval_response = await self.retrieval_use_case.execute(retrieval_request)

        # 2. Montagem de Contexto Fechado e Determinístico (Estágio 6)
        context_pack = self.context_builder.build_context_pack(retrieval_response)

        # 3. Geração Linguística Controlada (Estágio 7)
        raw_answer = await self.answer_generator.generate_answer(context_pack)

        # 4. Validação Rigorosa por Guardrails (Citações, Vigência, Proveniência e Conflitos) (Estágios 8 a 11)
        final_answer = LegalAnswerGuard.validate_and_enforce(raw_answer, context_pack)

        return final_answer
