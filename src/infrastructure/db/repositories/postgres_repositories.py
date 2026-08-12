from datetime import date
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.repositories import (
    EvidenceRepository,
    LegalDocumentRepository,
    LegalNodeRepository,
    LegalRelationRepository,
    LegalVersionRepository,
    SourceRepository,
)
from src.domain.entities.evidence import Evidence
from src.domain.entities.legal_document import LegalDocument
from src.domain.entities.legal_node import LegalNode
from src.domain.entities.legal_relation import LegalRelation
from src.domain.entities.legal_version import LegalVersion
from src.domain.entities.source import Source
from src.domain.enums import DocumentType, Jurisdiction, VersionStatus
from src.infrastructure.db.models.evidence_model import EvidenceModel
from src.infrastructure.db.models.legal_document_model import LegalDocumentModel
from src.infrastructure.db.models.legal_node_model import LegalNodeModel
from src.infrastructure.db.models.legal_relation_model import LegalRelationModel
from src.infrastructure.db.models.legal_version_model import LegalVersionModel
from src.infrastructure.db.models.source_model import SourceModel


# --- Mappers ---

def _source_to_domain(model: SourceModel) -> Source:
    return Source(
        id=model.id,
        name=model.name,
        official=model.official,
        authority_level=model.authority_level,
        base_url=model.base_url,
        jurisdiction=model.jurisdiction,
        active=model.active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _document_to_domain(model: LegalDocumentModel) -> LegalDocument:
    return LegalDocument(
        id=model.id,
        source_id=model.source_id,
        document_type=model.document_type,
        document_number=model.document_number,
        title=model.title,
        ementa=model.ementa,
        jurisdiction=model.jurisdiction,
        issuing_body=model.issuing_body,
        publication_date=model.publication_date,
        official_url=model.official_url,
        document_hash=model.document_hash,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _version_to_domain(model: LegalVersionModel) -> LegalVersion:
    return LegalVersion(
        id=model.id,
        legal_document_id=model.legal_document_id,
        version_number=model.version_number,
        content_hash=model.content_hash,
        published_at=model.published_at,
        effective_from=model.effective_from,
        effective_until=model.effective_until,
        status=model.status,
        source_document_url=model.source_document_url,
        raw_storage_key=model.raw_storage_key,
        parser_version=model.parser_version,
        created_at=model.created_at,
    )


def _node_to_domain(model: LegalNodeModel) -> LegalNode:
    return LegalNode(
        id=model.id,
        legal_version_id=model.legal_version_id,
        parent_id=model.parent_id,
        node_type=model.node_type,
        identifier=model.identifier,
        label=model.label,
        text=model.text,
        normalized_text=model.normalized_text,
        path=model.path,
        position=model.position,
        content_hash=model.content_hash,
        effective_from=model.effective_from,
        effective_until=model.effective_until,
        status=model.status,
        metadata=model.node_metadata or {},
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _relation_to_domain(model: LegalRelationModel) -> LegalRelation:
    return LegalRelation(
        id=model.id,
        source_node_id=model.source_node_id,
        target_node_id=model.target_node_id,
        relation_type=model.relation_type,
        effective_from=model.effective_from,
        effective_until=model.effective_until,
        confidence=model.confidence,
        evidence_id=model.evidence_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _evidence_to_domain(model: EvidenceModel) -> Evidence:
    return Evidence(
        id=model.id,
        source_id=model.source_id,
        legal_document_id=model.legal_document_id,
        legal_version_id=model.legal_version_id,
        legal_node_id=model.legal_node_id,
        source_url=model.source_url,
        quote_or_excerpt=model.quote_or_excerpt,
        locator=model.locator,
        content_hash=model.content_hash,
        captured_at=model.captured_at,
        created_at=model.created_at,
    )


# --- Repositories ---

class PostgresSourceRepository(SourceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, source_id: str) -> Optional[Source]:
        stmt = select(SourceModel).where(SourceModel.id == source_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _source_to_domain(model) if model else None

    async def save(self, source: Source) -> Source:
        model = SourceModel(
            id=source.id,
            name=source.name,
            official=source.official,
            authority_level=source.authority_level,
            base_url=source.base_url,
            jurisdiction=source.jurisdiction,
            active=source.active,
        )
        merged = await self.session.merge(model)
        await self.session.flush()
        return _source_to_domain(merged)

    async def list_active(self) -> List[Source]:
        stmt = select(SourceModel).where(SourceModel.active == True)
        result = await self.session.execute(stmt)
        return [_source_to_domain(m) for m in result.scalars().all()]


class PostgresLegalDocumentRepository(LegalDocumentRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, document_id: str) -> Optional[LegalDocument]:
        stmt = select(LegalDocumentModel).where(LegalDocumentModel.id == document_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _document_to_domain(model) if model else None

    async def find_by_number_and_type(
        self, document_number: str, document_type: DocumentType, jurisdiction: Jurisdiction
    ) -> List[LegalDocument]:
        stmt = select(LegalDocumentModel).where(
            LegalDocumentModel.document_number == document_number,
            LegalDocumentModel.document_type == document_type,
            LegalDocumentModel.jurisdiction == jurisdiction,
        )
        result = await self.session.execute(stmt)
        return [_document_to_domain(m) for m in result.scalars().all()]

    async def save(self, document: LegalDocument) -> LegalDocument:
        model = LegalDocumentModel(
            id=document.id,
            source_id=document.source_id,
            document_type=document.document_type,
            document_number=document.document_number,
            title=document.title,
            ementa=document.ementa,
            jurisdiction=document.jurisdiction,
            issuing_body=document.issuing_body,
            publication_date=document.publication_date,
            official_url=document.official_url,
            document_hash=document.document_hash,
        )
        merged = await self.session.merge(model)
        await self.session.flush()
        return _document_to_domain(merged)


class PostgresLegalVersionRepository(LegalVersionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, version_id: str) -> Optional[LegalVersion]:
        stmt = select(LegalVersionModel).where(LegalVersionModel.id == version_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _version_to_domain(model) if model else None

    async def get_effective_version(self, document_id: str, target_date: date) -> Optional[LegalVersion]:
        stmt = select(LegalVersionModel).where(
            LegalVersionModel.legal_document_id == document_id,
            LegalVersionModel.status == VersionStatus.ACTIVE,
            (LegalVersionModel.effective_from == None) | (LegalVersionModel.effective_from <= target_date),
            (LegalVersionModel.effective_until == None) | (LegalVersionModel.effective_until >= target_date),
        ).order_by(LegalVersionModel.version_number.desc())
        result = await self.session.execute(stmt)
        model = result.scalars().first()
        return _version_to_domain(model) if model else None

    async def save(self, version: LegalVersion) -> LegalVersion:
        model = LegalVersionModel(
            id=version.id,
            legal_document_id=version.legal_document_id,
            version_number=version.version_number,
            content_hash=version.content_hash,
            published_at=version.published_at,
            effective_from=version.effective_from,
            effective_until=version.effective_until,
            status=version.status,
            source_document_url=version.source_document_url,
            raw_storage_key=version.raw_storage_key,
            parser_version=version.parser_version,
        )
        merged = await self.session.merge(model)
        await self.session.flush()
        return _version_to_domain(merged)


class PostgresLegalNodeRepository(LegalNodeRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, node_id: str) -> Optional[LegalNode]:
        stmt = select(LegalNodeModel).where(LegalNodeModel.id == node_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _node_to_domain(model) if model else None

    async def get_children(self, parent_id: str) -> List[LegalNode]:
        stmt = select(LegalNodeModel).where(LegalNodeModel.parent_id == parent_id).order_by(LegalNodeModel.position.asc())
        result = await self.session.execute(stmt)
        return [_node_to_domain(m) for m in result.scalars().all()]

    async def get_tree_by_version(self, version_id: str) -> List[LegalNode]:
        stmt = select(LegalNodeModel).where(LegalNodeModel.legal_version_id == version_id).order_by(LegalNodeModel.position.asc())
        result = await self.session.execute(stmt)
        return [_node_to_domain(m) for m in result.scalars().all()]

    async def save(self, node: LegalNode) -> LegalNode:
        model = LegalNodeModel(
            id=node.id,
            legal_version_id=node.legal_version_id,
            parent_id=node.parent_id,
            node_type=node.node_type,
            identifier=node.identifier,
            label=node.label,
            text=node.text,
            normalized_text=node.normalized_text,
            path=node.path,
            position=node.position,
            content_hash=node.content_hash,
            effective_from=node.effective_from,
            effective_until=node.effective_until,
            status=node.status,
            node_metadata=node.metadata,
        )
        merged = await self.session.merge(model)
        await self.session.flush()
        return _node_to_domain(merged)

    async def save_bulk(self, nodes: List[LegalNode]) -> None:
        for node in nodes:
            await self.save(node)


class PostgresLegalRelationRepository(LegalRelationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, relation_id: str) -> Optional[LegalRelation]:
        stmt = select(LegalRelationModel).where(LegalRelationModel.id == relation_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _relation_to_domain(model) if model else None

    async def get_relations_from(self, source_node_id: str) -> List[LegalRelation]:
        stmt = select(LegalRelationModel).where(LegalRelationModel.source_node_id == source_node_id)
        result = await self.session.execute(stmt)
        return [_relation_to_domain(m) for m in result.scalars().all()]

    async def get_relations_to(self, target_node_id: str) -> List[LegalRelation]:
        stmt = select(LegalRelationModel).where(LegalRelationModel.target_node_id == target_node_id)
        result = await self.session.execute(stmt)
        return [_relation_to_domain(m) for m in result.scalars().all()]

    async def save(self, relation: LegalRelation) -> LegalRelation:
        model = LegalRelationModel(
            id=relation.id,
            source_node_id=relation.source_node_id,
            target_node_id=relation.target_node_id,
            relation_type=relation.relation_type,
            effective_from=relation.effective_from,
            effective_until=relation.effective_until,
            confidence=relation.confidence,
            evidence_id=relation.evidence_id,
        )
        merged = await self.session.merge(model)
        await self.session.flush()
        return _relation_to_domain(merged)


class PostgresEvidenceRepository(EvidenceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, evidence_id: str) -> Optional[Evidence]:
        stmt = select(EvidenceModel).where(EvidenceModel.id == evidence_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _evidence_to_domain(model) if model else None

    async def get_by_hash(self, content_hash: str) -> Optional[Evidence]:
        stmt = select(EvidenceModel).where(EvidenceModel.content_hash == content_hash)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return _evidence_to_domain(model) if model else None

    async def save(self, evidence: Evidence) -> Evidence:
        model = EvidenceModel(
            id=evidence.id,
            source_id=evidence.source_id,
            legal_document_id=evidence.legal_document_id,
            legal_version_id=evidence.legal_version_id,
            legal_node_id=evidence.legal_node_id,
            source_url=evidence.source_url,
            quote_or_excerpt=evidence.quote_or_excerpt,
            locator=evidence.locator,
            content_hash=evidence.content_hash,
            captured_at=evidence.captured_at,
        )
        merged = await self.session.merge(model)
        await self.session.flush()
        return _evidence_to_domain(merged)
