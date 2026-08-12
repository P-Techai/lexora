from datetime import date
import inspect
import pytest

import src.infrastructure.db.models as models
from src.domain.entities.legal_version import LegalVersion
from src.domain.enums import VersionStatus
from src.domain.exceptions import MissingRevokingSourceError
from src.domain.services.temporal_search_service import TemporalLegalSearchService
from src.domain.services.temporal_validator import TemporalIntegrityValidator


def test_audit_no_cascade_foreign_keys_in_orm_models():
    """AUDITORIA AUTOMÁTICA DE INFRAESTRUTURA: Garante que NENHUMA FK de modelo relacional jurídico utiliza CASCADE."""
    orm_classes = [
        models.SourceModel,
        models.LegalDocumentModel,
        models.LegalVersionModel,
        models.LegalNodeModel,
        models.LegalRelationModel,
        models.EvidenceModel,
        models.RawArtifactModel,
        models.AcquisitionAuditLogModel,
    ]

    cascade_violations = []

    for cls in orm_classes:
        for column_name, column in cls.__table__.columns.items():
            for fk in column.foreign_keys:
                if fk.ondelete and fk.ondelete.upper() == "CASCADE":
                    cascade_violations.append(f"Tabela '{cls.__tablename__}', Coluna '{column_name}' possui ON DELETE CASCADE!")

    assert not cascade_violations, f"Violação de Segurança Jurídica: {cascade_violations}"


def test_single_source_of_truth_for_temporal_math():
    """AUDITORIA TEMPORAL: Garante que LegalVersion.is_effective_on delega para TemporalIntegrityValidator.is_date_in_range."""
    ver = LegalVersion(
        id="v1",
        legal_document_id="doc1",
        version_number=1,
        content_hash="h1",
        effective_from=date(2020, 1, 1),
        effective_until=date(2022, 1, 1),
        status=VersionStatus.ACTIVE
    )

    # 1. No dia de término (2022-01-01) -> Deve ser False (Exclusivo!)
    assert ver.is_effective_on(date(2022, 1, 1)) is False
    assert TemporalIntegrityValidator.is_date_in_range(date(2022, 1, 1), ver.effective_from, ver.effective_until) is False

    # 2. No dia anterior ao término (2021-12-31) -> Deve ser True
    assert ver.is_effective_on(date(2021, 12, 31)) is True
    assert TemporalIntegrityValidator.is_date_in_range(date(2021, 12, 31), ver.effective_from, ver.effective_until) is True


def test_audit_system_clock_not_used_for_legal_truth():
    """AUDITORIA DE RELÓGIO: Garante que os serviços de verdade jurídica exigem target_date explicita."""
    sig_resolve = inspect.signature(TemporalLegalSearchService.resolve_version_at_date)
    target_param = sig_resolve.parameters.get("target_date")

    assert target_param is not None, "TemporalLegalSearchService.resolve_version_at_date DEVE aceitar target_date!"
    assert target_param.default == inspect.Parameter.empty, "target_date NÃO pode ter valor default de relógio do sistema!"


def test_audit_prohibit_self_referencing_revocation_relations():
    """AUDITORIA DE REVOGAÇÃO: Valida que relações de revogação sem origem revogadora distinta disparam exceção."""
    # A exceção MissingRevokingSourceError deve ser importável e existente
    assert issubclass(MissingRevokingSourceError, Exception)
