import uuid
from typing import Optional, Tuple

from src.application.ports.repositories import LegalDocumentRepository, LegalVersionRepository
from src.domain.entities.legal_version import LegalVersion
from src.domain.enums import VersionStatus
from src.domain.exceptions import InvalidEffectivePeriodError, InvalidLegalDocumentError


class CreateVersionUseCase:
    """Caso de uso para criar uma nova versão histórica LegalVersion."""

    def __init__(self, version_repo: LegalVersionRepository, doc_repo: LegalDocumentRepository):
        self.version_repo = version_repo
        self.doc_repo = doc_repo

    async def execute(
        self,
        legal_document_id: str,
        content_hash: str,
        published_at=None,
        effective_from=None,
        effective_until=None,
        status: VersionStatus = VersionStatus.ACTIVE,
        source_document_url: Optional[str] = None,
        raw_storage_key: Optional[str] = None,
        parser_version: str = "1.0.0"
    ) -> Tuple[LegalVersion, bool]:
        """Cria uma versão se o hash do conteúdo mudou. Retorna (LegalVersion, created_flag)."""
        doc = await self.doc_repo.get_by_id(legal_document_id)
        if not doc:
            raise InvalidLegalDocumentError(f"LegalDocument com ID '{legal_document_id}' não existe.")

        if effective_from and effective_until and effective_until < effective_from:
            raise InvalidEffectivePeriodError("Data de término de vigência (effective_until) não pode ser anterior ao início (effective_from).")

        # Verifica se já existe versão com o mesmo hash para o documento (idempotência)
        if published_at:
            existing = await self.version_repo.get_effective_version(legal_document_id, published_at)
            if existing and existing.content_hash == content_hash:
                return existing, False

        version = LegalVersion(
            id=str(uuid.uuid4()),
            legal_document_id=legal_document_id,
            version_number=1,  # incrementado pelo repositório se necessário
            content_hash=content_hash,
            published_at=published_at,
            effective_from=effective_from,
            effective_until=effective_until,
            status=status,
            source_document_url=source_document_url,
            raw_storage_key=raw_storage_key,
            parser_version=parser_version
        )

        saved = await self.version_repo.save(version)
        return saved, True
