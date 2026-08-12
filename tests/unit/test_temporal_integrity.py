from datetime import date
import pytest

from src.domain.entities.legal_version import LegalVersion
from src.domain.enums import TemporalStatus, VersionStatus
from src.domain.exceptions import InvalidEffectivePeriodError
from src.domain.services.temporal_validator import TemporalIntegrityValidator


def test_invalid_period_exception():
    # effective_until anterior a effective_from
    invalid_ver = LegalVersion(
        id="v-inv",
        legal_document_id="doc-1",
        version_number=1,
        content_hash="hi",
        effective_from=date(2024, 6, 1),
        effective_until=date(2024, 1, 1),  # ANTERIOR!
        status=VersionStatus.ACTIVE
    )

    with pytest.raises(InvalidEffectivePeriodError):
        TemporalIntegrityValidator.validate_version_period(invalid_ver)


def test_audit_version_series_overlap_detection():
    # Versão A: [2024-01-01, 2024-06-01)
    ver_a = LegalVersion(
        id="v-a",
        legal_document_id="doc-1",
        version_number=1,
        content_hash="ha",
        effective_from=date(2024, 1, 1),
        effective_until=date(2024, 6, 1),
        status=VersionStatus.ACTIVE
    )

    # Versão B: [2024-05-01, 2024-12-01) - SOBREPOSIÇÃO com A de maio a junho!
    ver_b = LegalVersion(
        id="v-b",
        legal_document_id="doc-1",
        version_number=2,
        content_hash="hb",
        effective_from=date(2024, 5, 1),
        effective_until=date(2024, 12, 1),
        status=VersionStatus.ACTIVE
    )

    status, warnings = TemporalIntegrityValidator.audit_version_series([ver_a, ver_b])
    assert status == TemporalStatus.TEMPORAL_CONFLICT
    assert any("CONFLITO TEMPORAL" in w for w in warnings)


def test_audit_version_series_gap_detection():
    # Versão A: [2020-01-01, 2022-01-01)
    ver_a = LegalVersion(
        id="v-a",
        legal_document_id="doc-1",
        version_number=1,
        content_hash="ha",
        effective_from=date(2020, 1, 1),
        effective_until=date(2022, 1, 1),
        status=VersionStatus.ACTIVE
    )

    # Versão B: [2022-06-01, NULL) - LACUNA (GAP) de Jan a Jun 2022!
    ver_b = LegalVersion(
        id="v-b",
        legal_document_id="doc-1",
        version_number=2,
        content_hash="hb",
        effective_from=date(2022, 6, 1),
        effective_until=None,
        status=VersionStatus.ACTIVE
    )

    status, warnings = TemporalIntegrityValidator.audit_version_series([ver_a, ver_b])
    assert status == TemporalStatus.TEMPORAL_GAP
    assert any("GAP TEMPORAL" in w for w in warnings)
