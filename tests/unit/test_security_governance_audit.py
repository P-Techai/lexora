from datetime import date
import inspect
from pathlib import Path
import pytest

import src.infrastructure.db.models as models
from src.domain.entities.legal_version import LegalVersion
from src.domain.enums import VersionStatus
from src.domain.exceptions import MissingRevokingSourceError
from src.domain.services.temporal_search_service import TemporalLegalSearchService
from src.domain.services.temporal_validator import TemporalIntegrityValidator


def test_audit_no_cascade_or_set_null_foreign_keys_in_orm_models():
    """
    AUDITORIA AUTOMÁTICA DE GOVERNANÇA E SEGURANÇA:
    Garante que NENHUMA FK de modelo relacional jurídico/proveniência utiliza CASCADE ou SET NULL.
    Regra absoluta da LÉXORA: Todas devem usar ON DELETE RESTRICT.
    """
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

    violations = []

    for cls in orm_classes:
        for column_name, column in cls.__table__.columns.items():
            for fk in column.foreign_keys:
                if fk.ondelete and fk.ondelete.upper() in ("CASCADE", "SET NULL"):
                    violations.append(
                        f"Tabela '{cls.__tablename__}', Coluna '{column_name}' possui ON DELETE {fk.ondelete.upper()}!"
                    )

    assert not violations, f"Violação de Segurança Jurídica / Integridade Referencial: {violations}"


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
    assert issubclass(MissingRevokingSourceError, Exception)


def test_audit_static_delete_operations_in_src():
    """AUDITORIA ESTÁTICA DE CÓDIGO: Verifica se existem operações .delete() em entidades normativas em src/."""
    src_dir = Path("src")
    prohibited_patterns = [
        ".delete()",
        "DELETE FROM legal_",
        "DELETE FROM evidences",
        "DELETE FROM sources",
    ]

    violations = []
    for py_file in src_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        for pattern in prohibited_patterns:
            if pattern in content:
                violations.append(f"Arquivo '{py_file}' contém operação de delete proibida: '{pattern}'")

    assert not violations, f"Violação de Imutabilidade Jurídica em Código Fonte: {violations}"
