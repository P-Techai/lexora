from typing import Optional

from src.application.dto.ingestion_dto import (
    IngestionStatus,
    LegalDocumentIngestionRequest,
    LegalDocumentIngestionResult,
)
from src.application.ports.repositories import (
    LegalDocumentRepository,
    LegalNodeRepository,
    LegalVersionRepository,
    SourceRepository,
)

from src.application.ports.storage_provider import StorageProvider
from src.application.ports.structure_parser import LegalStructureParser
from src.application.use_cases.legal.add_legal_nodes import AddLegalNodesUseCase
from src.application.use_cases.legal.create_document import CreateDocumentUseCase
from src.application.use_cases.legal.create_version import CreateVersionUseCase

from src.domain.services.hash_service import DocumentHashCalculator
from src.domain.services.normalization_service import LegalNormalizationService


class IngestDocumentUseCase:
    """
    Orquestrador do Pipeline Determinístico de Ingestão Jurídica de 7 Estágios:
    RAW CONTENT -> HASH -> NORMALIZAÇÃO -> VALIDAÇÃO DE METADADOS -> PARSER ESTRUTURAL -> VALIDAÇÃO DE ÁRVORE -> PERSISTÊNCIA TRANSECCIONADA
    """

    def __init__(
        self,
        source_repo: SourceRepository,
        doc_repo: LegalDocumentRepository,
        version_repo: LegalVersionRepository,
        node_repo: LegalNodeRepository,
        structure_parser: LegalStructureParser,
        storage_provider: Optional[StorageProvider] = None
    ):
        self.source_repo = source_repo
        self.doc_repo = doc_repo
        self.version_repo = version_repo
        self.node_repo = node_repo
        self.structure_parser = structure_parser
        self.storage_provider = storage_provider

        self.create_doc_uc = CreateDocumentUseCase(doc_repo, source_repo)
        self.create_ver_uc = CreateVersionUseCase(version_repo, doc_repo)
        self.add_nodes_uc = AddLegalNodesUseCase(node_repo, version_repo)

    async def execute(
        self,
        request: LegalDocumentIngestionRequest,
        dry_run: bool = False
    ) -> LegalDocumentIngestionResult:
        errors = []
        warnings = []

        # 1. Estágio: Cálculo de Hash do Conteúdo Raw
        content_hash = DocumentHashCalculator.calculate_sha256(request.raw_content)

        # 2. Estágio: Normalização sem alterar o significado jurídico
        normalized_content = LegalNormalizationService.normalize_text(request.raw_content)

        # 3. Estágio: Validação de Metadados e Origem
        source = await self.source_repo.get_by_id(request.source_id)
        if not source:
            errors.append(f"Origem (Source) '{request.source_id}' não cadastrada.")
            return LegalDocumentIngestionResult(
                status=IngestionStatus.REJECTED,
                content_hash=content_hash,
                validation_errors=errors
            )

        # 4. Estágio: Verificação de Idempotência
        existing_docs = await self.doc_repo.find_by_number_and_type(
            document_number=request.document_number,
            document_type=request.document_type,
            jurisdiction=request.jurisdiction
        )

        existing_doc = None
        for doc in existing_docs:
            if doc.source_id == request.source_id:
                existing_doc = doc
                break

        if existing_doc:
            effective_ver = await self.version_repo.get_effective_version(
                existing_doc.id,
                request.publication_date or request.captured_at.date()
            )
            if effective_ver and effective_ver.content_hash == content_hash:
                warnings.append("Documento com hash idêntico já cadastrado sem alterações.")
                return LegalDocumentIngestionResult(
                    status=IngestionStatus.DUPLICATE,
                    document_id=existing_doc.id,
                    version_id=effective_ver.id,
                    content_hash=content_hash,
                    duplicate=True,
                    warnings=warnings
                )

        # Se modo dry_run=True, valida e retorna diagnóstico sem persistir no banco
        if dry_run:
            dummy_ver_id = "dry-run-ver-id"
            try:
                nodes = self.structure_parser.parse_structure(normalized_content, dummy_ver_id)
            except Exception as e:
                errors.append(f"Erro no parser estrutural: {str(e)}")
                return LegalDocumentIngestionResult(
                    status=IngestionStatus.REJECTED,
                    content_hash=content_hash,
                    validation_errors=errors
                )

            return LegalDocumentIngestionResult(
                status=IngestionStatus.CREATED,
                content_hash=content_hash,
                created=False,
                warnings=["DRY RUN: Diagnóstico concluído com sucesso sem gravação em banco."]
            )

        # 5. Estágio: Persistência Transacional do Documento e Versão
        document, doc_created = await self.create_doc_uc.execute(
            source_id=request.source_id,
            document_type=request.document_type,
            document_number=request.document_number,
            title=request.title,
            ementa=request.ementa,
            jurisdiction=request.jurisdiction,
            issuing_body=request.issuing_body,
            publication_date=request.publication_date,
            official_url=request.official_url,
            document_hash=content_hash
        )

        raw_key = None
        if self.storage_provider:
            raw_key = f"raw/{request.source_id}/{request.document_number}/{content_hash}.txt"
            await self.storage_provider.save_bytes(raw_key, request.raw_content.encode("utf-8"), request.content_type)

        version, ver_created = await self.create_ver_uc.execute(
            legal_document_id=document.id,
            content_hash=content_hash,
            published_at=request.publication_date,
            effective_from=request.publication_date,
            source_document_url=request.official_url,
            raw_storage_key=raw_key
        )

        # 6. Estágio: Parsing e Estruturação de Nós Normativos
        nodes = self.structure_parser.parse_structure(normalized_content, version.id)

        # 7. Estágio: Validação da Árvore e Persistência dos Nós
        await self.add_nodes_uc.execute(version.id, nodes)

        status = IngestionStatus.CREATED if doc_created else IngestionStatus.UPDATED

        return LegalDocumentIngestionResult(
            status=status,
            document_id=document.id,
            version_id=version.id,
            content_hash=content_hash,
            created=doc_created,
            duplicate=False,
            warnings=warnings
        )
