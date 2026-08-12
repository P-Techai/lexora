from datetime import date
import pytest

from src.domain.entities.legal_document import LegalDocument
from src.domain.entities.source import Source
from src.domain.enums import (
    ChangeStatus,
    DocumentType,
    IdentityMatchStatus,
    Jurisdiction,
    SourcePolicy,
)
from src.domain.exceptions import SSRFProtectionError, UrlNotAllowedError
from src.domain.services.change_detection import ChangeDetectionService
from src.domain.services.hash_service import DocumentHashCalculator
from src.domain.services.identity_matcher import DocumentIdentityMatcher
from src.domain.services.url_validator import URLSecurityValidator


def test_url_security_validator_allowed_domains():
    allowed = ["planalto.gov.br", "receita.fazenda.gov.br"]

    # URLs válidas
    url1 = "https://www.planalto.gov.br/ccivil_03/leis/l8112.htm"
    url2 = "https://receita.fazenda.gov.br/normas/in123.htm"

    assert URLSecurityValidator.validate_url(url1, allowed_domains=allowed) == url1
    assert URLSecurityValidator.validate_url(url2, allowed_domains=allowed) == url2

    # Domínio não permitido
    with pytest.raises(UrlNotAllowedError):
        URLSecurityValidator.validate_url("https://blog-nao-oficial.com/lei", allowed_domains=allowed)


def test_url_security_validator_ssrf_protection():
    # 1. Localhost e Loopback
    with pytest.raises(SSRFProtectionError):
        URLSecurityValidator.validate_url("http://localhost:8080/secret")
    with pytest.raises(SSRFProtectionError):
        URLSecurityValidator.validate_url("http://127.0.0.1/admin")
    with pytest.raises(SSRFProtectionError):
        URLSecurityValidator.validate_url("http://0.0.0.0/config")

    # 2. Subredes Privadas (10.x, 172.16.x, 192.168.x)
    with pytest.raises(SSRFProtectionError):
        URLSecurityValidator.validate_url("http://10.0.0.1/internal")
    with pytest.raises(SSRFProtectionError):
        URLSecurityValidator.validate_url("http://172.16.0.5/private")
    with pytest.raises(SSRFProtectionError):
        URLSecurityValidator.validate_url("http://192.168.1.254/router")

    # 3. Metadata Endpoint de Nuvem
    with pytest.raises(SSRFProtectionError):
        URLSecurityValidator.validate_url("http://169.254.169.254/latest/meta-data/")

    # 4. Esquema inválido (ftp, file, gopher)
    with pytest.raises(UrlNotAllowedError):
        URLSecurityValidator.validate_url("file:///etc/passwd")


def test_change_detection_service():
    hash1 = DocumentHashCalculator.calculate_sha256("Texto A")
    hash2 = DocumentHashCalculator.calculate_sha256("Texto A")
    hash3 = DocumentHashCalculator.calculate_sha256("Texto B")

    assert ChangeDetectionService.detect_change(hash1, None) == ChangeStatus.NEW
    assert ChangeDetectionService.detect_change(hash1, hash2) == ChangeStatus.UNCHANGED
    assert ChangeDetectionService.detect_change(hash1, hash3) == ChangeStatus.CHANGED


def test_document_identity_matcher():
    doc_a = LegalDocument(
        id="doc-1",
        source_id="src-planalto",
        document_type=DocumentType.ORDINARY_LAW,
        document_number="8112",
        title="Lei 8112",
        jurisdiction=Jurisdiction.FEDERAL,
        issuing_body="PRESIDENCIA",
        document_hash="h1"
    )

    # Identidade Exata
    match_exact = DocumentIdentityMatcher.match_document_identity(
        doc_a=doc_a,
        source_id="src-planalto",
        document_type=DocumentType.ORDINARY_LAW,
        document_number="8112",
        jurisdiction=Jurisdiction.FEDERAL,
        issuing_body="PRESIDENCIA"
    )
    assert match_exact == IdentityMatchStatus.EXACT_MATCH

    # Mesma lei vinda de outra fonte (Possível correspondência)
    match_possible = DocumentIdentityMatcher.match_document_identity(
        doc_a=doc_a,
        source_id="src-diario-oficial",
        document_type=DocumentType.ORDINARY_LAW,
        document_number="8112",
        jurisdiction=Jurisdiction.FEDERAL,
        issuing_body="PRESIDENCIA"
    )
    assert match_possible == IdentityMatchStatus.POSSIBLE_MATCH

    # Documento completamente diferente
    match_none = DocumentIdentityMatcher.match_document_identity(
        doc_a=doc_a,
        source_id="src-planalto",
        document_type=DocumentType.ORDINARY_LAW,
        document_number="9999",
        jurisdiction=Jurisdiction.FEDERAL
    )
    assert match_none == IdentityMatchStatus.NO_MATCH
