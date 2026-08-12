from datetime import date
import pytest

from src.domain.entities.legal_version import LegalVersion
from src.domain.enums import TemporalStatus, VersionStatus
from src.domain.services.temporal_search_service import TemporalLegalSearchService
from src.domain.services.temporal_validator import TemporalIntegrityValidator


def test_half_open_interval_boundary_math():
    # Semântica [2024-01-01, 2024-07-01)
    effective_from = date(2024, 1, 1)
    effective_until = date(2024, 7, 1)

    # 1. Data anterior ao início -> False
    assert TemporalIntegrityValidator.is_date_in_range(date(2023, 12, 31), effective_from, effective_until) is False

    # 2. Exatamente na data de início (effective_from) -> True (Inclusivo)
    assert TemporalIntegrityValidator.is_date_in_range(date(2024, 1, 1), effective_from, effective_until) is True

    # 3. No meio do período -> True
    assert TemporalIntegrityValidator.is_date_in_range(date(2024, 6, 30), effective_from, effective_until) is True

    # 4. Exatamente na data de término (effective_until) -> False (Exclusivo!)
    assert TemporalIntegrityValidator.is_date_in_range(date(2024, 7, 1), effective_from, effective_until) is False

    # 5. Data posterior ao término -> False
    assert TemporalIntegrityValidator.is_date_in_range(date(2024, 7, 2), effective_from, effective_until) is False


def test_consecutive_versions_resolution():
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

    # Versão B: [2022-01-01, 2024-01-01)
    ver_b = LegalVersion(
        id="v-b",
        legal_document_id="doc-1",
        version_number=2,
        content_hash="hb",
        effective_from=date(2022, 1, 1),
        effective_until=date(2024, 1, 1),
        status=VersionStatus.ACTIVE
    )

    # Versão C: [2024-01-01, NULL) - Vigência aberta
    ver_c = LegalVersion(
        id="v-c",
        legal_document_id="doc-1",
        version_number=3,
        content_hash="hc",
        effective_from=date(2024, 1, 1),
        effective_until=None,
        status=VersionStatus.ACTIVE
    )

    versions = [ver_a, ver_b, ver_c]

    # Em 2020 -> Versão A
    st_20, ver_20, _ = TemporalLegalSearchService.resolve_version_at_date(versions, date(2020, 6, 1))
    assert st_20 == TemporalStatus.EFFECTIVE
    assert ver_20.id == "v-a"

    # Em 2021-12-31 -> Versão A
    st_21, ver_21, _ = TemporalLegalSearchService.resolve_version_at_date(versions, date(2021, 12, 31))
    assert st_21 == TemporalStatus.EFFECTIVE
    assert ver_21.id == "v-a"

    # Em 2022-01-01 -> Transição exata para Versão B
    st_22, ver_22, _ = TemporalLegalSearchService.resolve_version_at_date(versions, date(2022, 1, 1))
    assert st_22 == TemporalStatus.EFFECTIVE
    assert ver_22.id == "v-b"

    # Em 2024-01-01 -> Transição exata para Versão C
    st_24, ver_24, _ = TemporalLegalSearchService.resolve_version_at_date(versions, date(2024, 1, 1))
    assert st_24 == TemporalStatus.EFFECTIVE
    assert ver_24.id == "v-c"

    # Em 2030 -> Versão C continua vigente (vigência aberta)
    st_30, ver_30, _ = TemporalLegalSearchService.resolve_version_at_date(versions, date(2030, 1, 1))
    assert st_30 == TemporalStatus.EFFECTIVE
    assert ver_30.id == "v-c"


def test_vacatio_legis_resolution():
    ver_future = LegalVersion(
        id="v-fut",
        legal_document_id="doc-1",
        version_number=1,
        content_hash="hf",
        effective_from=date(2030, 1, 1),
        status=VersionStatus.ACTIVE
    )

    st, ver, warnings = TemporalLegalSearchService.resolve_version_at_date([ver_future], date(2026, 1, 1))
    assert st == TemporalStatus.NOT_YET_EFFECTIVE
    assert ver is None
    assert "vigência inicia em 2030-01-01" in warnings[0]
