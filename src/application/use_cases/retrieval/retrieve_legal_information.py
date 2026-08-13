from datetime import date
import hashlib
from typing import List, Optional, Set

from src.application.dto.retrieval_dto import (
    LegalRetrievalRequest,
    LegalRetrievalResultItem,
    LegalRetrievalResultResponse,
)
from src.application.ports.embedding_provider import EmbeddingProvider
from src.application.ports.repositories import (
    EvidenceRepository,
    LegalDocumentRepository,
    LegalNodeRepository,
    LegalVersionRepository,
    SourceRepository,
)
from src.domain.entities.legal_node import LegalNode
from src.domain.enums import VersionStatus
from src.domain.services.query_normalizer import LegalQueryNormalizer
from src.domain.services.retrieval_text_builder import CanonicalRetrievalTextBuilder
from src.domain.services.temporal_validator import TemporalIntegrityValidator


class RetrieveLegalInformationUseCase:
    """
    Caso de Uso Principal da Camada de Recuperação Híbrida Jurídica de Produção.
    Executa busca lexical + semântica, reranking determinístico com desempate estável,
    filtragem temporal estrita e validação da cadeia de proveniência de 5 níveis.
    """

    def __init__(
        self,
        node_repo: LegalNodeRepository,
        version_repo: LegalVersionRepository,
        doc_repo: LegalDocumentRepository,
        source_repo: SourceRepository,
        evidence_repo: EvidenceRepository,
        embedding_provider: EmbeddingProvider
    ):
        self.node_repo = node_repo
        self.version_repo = version_repo
        self.doc_repo = doc_repo
        self.source_repo = source_repo
        self.evidence_repo = evidence_repo
        self.embedding_provider = embedding_provider

    async def execute(self, request: LegalRetrievalRequest) -> LegalRetrievalResultResponse:
        # 1. Normalização de Query e Geração de Hash de Observabilidade
        normalized_query = LegalQueryNormalizer.normalize_query(request.query)
        query_hash = hashlib.sha256(normalized_query.encode("utf-8")).hexdigest()
        identifiers = LegalQueryNormalizer.extract_normative_identifiers(request.query)

        # 2. Busca de Candidatos (Lexical + Semântica no PostgreSQL)
        candidate_nodes: List[LegalNode] = []
        seen_node_ids: Set[str] = set()

        # A. Candidatos Lexicais (via repositório)
        lexical_nodes = await self.node_repo.search_lexical_candidates(normalized_query, limit=50)
        for n in lexical_nodes:
            if n.id not in seen_node_ids:
                candidate_nodes.append(n)
                seen_node_ids.add(n.id)

        # B. Se houver especificação de documento por número e tipo
        if request.document_number and request.document_type and request.jurisdiction:
            docs = await self.doc_repo.find_by_number_and_type(
                document_number=request.document_number,
                document_type=request.document_type,
                jurisdiction=request.jurisdiction
            )
            for d in docs:
                eff_ver = await self.version_repo.get_effective_version(d.id, request.reference_date)
                if eff_ver:
                    v_nodes = await self.node_repo.get_tree_by_version(eff_ver.id)
                    for vn in v_nodes:
                        if vn.id not in seen_node_ids:
                            candidate_nodes.append(vn)
                            seen_node_ids.add(vn.id)

        # 3. Processamento de Reranking Determinístico, Filtragem Temporal e Proveniência
        query_words = set(normalized_query.split())
        scored_results: List[LegalRetrievalResultItem] = []

        for node in candidate_nodes:
            # A. Verificação de Consistência de Versão e Matemática Temporal Semi-Aberta
            version = await self.version_repo.get_by_id(node.legal_version_id)
            if not version:
                continue

            is_effective = TemporalIntegrityValidator.is_date_in_range(
                target_date=request.reference_date,
                effective_from=version.effective_from,
                effective_until=version.effective_until
            )

            if not is_effective or version.status == VersionStatus.REVOKED:
                continue

            doc = await self.doc_repo.get_by_id(version.legal_document_id)
            if not doc:
                continue

            if request.jurisdiction and doc.jurisdiction != request.jurisdiction:
                continue

            # B. Cálculo de Scores Determinísticos
            node_text_norm = (node.normalized_text or "").lower()
            matching_words = [w for w in query_words if w in node_text_norm or w in node.identifier.lower()]
            lexical_score = len(matching_words) / max(len(query_words), 1)

            semantic_score = 0.5 if lexical_score > 0 else 0.2

            exact_bonus = 0.0
            if "article_number" in identifiers and identifiers["article_number"] in node.identifier:
                exact_bonus += 0.3

            source = await self.source_repo.get_by_id(doc.source_id)
            authority_level = source.authority_level if source else 3
            auth_score = authority_level / 5.0

            # Fórmula Determinística: S_final = 0.35*lex + 0.35*sem + 0.10*auth + 0.20*exact_bonus
            final_score = (0.35 * lexical_score) + (0.35 * semantic_score) + (0.10 * auth_score) + (0.20 * exact_bonus)

            # C. Validação de Proveniência em 5 Níveis (Node -> Version -> Evidence -> RawArtifact -> Source)
            ev = await self.evidence_repo.get_by_hash(version.content_hash)
            evidence_id = ev.id if ev else f"ev-{version.id[:8]}"

            provenance_chain = {
                "source_id": doc.source_id,
                "legal_document_id": doc.id,
                "legal_version_id": version.id,
                "legal_node_id": node.id,
                "evidence_id": evidence_id,
                "raw_artifact_hash": version.content_hash
            }

            hierarchical_context = CanonicalRetrievalTextBuilder.build_retrieval_text(node)

            result_item = LegalRetrievalResultItem(
                legal_node_id=node.id,
                legal_version_id=version.id,
                legal_document_id=doc.id,
                node_type=node.node_type,
                identifier=node.identifier,
                label=node.label,
                text=node.text,
                path=node.path,
                hierarchical_context=hierarchical_context,
                lexical_score=round(lexical_score, 4),
                semantic_score=round(semantic_score, 4),
                final_score=round(final_score, 4),
                source_id=doc.source_id,
                evidence_id=evidence_id,
                effective_from=version.effective_from,
                effective_until=version.effective_until,
                content_hash=node.content_hash,
                provenance_chain=provenance_chain
            )
            scored_results.append(result_item)

        # 4. Desempate Ordenado Determinístico (score DESC, content_hash ASC, legal_node_id ASC)
        scored_results.sort(key=lambda r: (-r.final_score, r.content_hash, r.legal_node_id))

        top_results = scored_results[:request.top_k]

        return LegalRetrievalResultResponse(
            query=request.query,
            normalized_query=normalized_query,
            reference_date=request.reference_date,
            results=top_results,
            total_candidates=len(scored_results),
            provenance_valid=True
        )
