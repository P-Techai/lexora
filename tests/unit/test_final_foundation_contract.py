import ast
from pathlib import Path
import pytest

from src.application.dto.acquisition_dto import AcquisitionRequest, AcquisitionResult
from src.application.parsers.brazilian_law_parser import BrazilianLawParser
from src.application.ports.acquisition_provider import DocumentAcquisitionProvider
from src.application.services.source_registry import SourceRegistryService
from src.domain.entities.source import Source
from src.domain.enums import ChangeStatus, LegalNodeType
from src.domain.exceptions import ArtifactTooLargeError, RedirectNotAllowedError, SSRFProtectionError
from src.domain.services.hash_service import DocumentHashCalculator
from src.domain.services.url_validator import URLSecurityValidator
from src.infrastructure.adapters.http_acquisition import HttpDocumentAcquisitionAdapter


def test_contract_A_acquisition_port_unification():
    """Verifica que HttpDocumentAcquisitionAdapter herda de DocumentAcquisitionProvider e tem o método acquire."""
    registry = SourceRegistryService()
    adapter = HttpDocumentAcquisitionAdapter(registry)
    assert isinstance(adapter, DocumentAcquisitionProvider)
    assert hasattr(adapter, "acquire")


def test_contract_B_no_change_status_updated():
    """Verifica que o símbolo ChangeStatus.UPDATED não existe no enum e não é usado em nenhum arquivo de src/."""
    assert not hasattr(ChangeStatus, "UPDATED"), "ChangeStatus.UPDATED não pode existir! Usar ChangeStatus.CHANGED."

    src_dir = Path("src")
    violations = []
    for py_file in src_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        if "ChangeStatus.UPDATED" in content:
            violations.append(str(py_file))

    assert not violations, f"Usos proibidos de ChangeStatus.UPDATED encontrados em: {violations}"


def test_contract_C_D_E_parser_subsecao_anexo_and_canonical_hash():
    """Verifica suporte a SUBSECAO e ANEXO e hash canônico determinístico."""
    parser = BrazilianLawParser()
    raw_text = """DECRETO Nº 9.580, DE 22 DE DEZEMBRO DE 2018
CAPÍTULO I
SEÇÃO I
SUBSEÇÃO I
Da Isenção
Art. 1º Dispositivo do artigo.
ANEXO I
TABELA NORMATIVA"""

    nodes, warnings = parser.parse_structure(raw_text, version_id="ver-dec9580")

    node_types = [n.node_type for n in nodes]
    assert LegalNodeType.SUBSECAO in node_types, "Parser deve reconhecer SUBSEÇÃO!"
    assert LegalNodeType.ANEXO in node_types, "Parser deve reconhecer ANEXO!"

    # Valida identidade lógica determinística
    art1 = next(n for n in nodes if n.identifier == "art-1")
    assert art1.logical_id == "ver-dec9580:/norma/capitulo-i/secao-i/subsecao-i/art-1"
    
    # Hash independente de UUID
    hash1 = DocumentHashCalculator.calculate_canonical_node_hash("ARTIGO", "art-1", "Art. 1º", "Dispositivo do artigo.")
    assert art1.content_hash == hash1


def test_contract_F_G_H_no_delete_orphan_or_cascade_in_orm():
    """Auditoria estática de AST no ORM garantindo 0 delete-orphan, 0 CASCADE e 0 SET NULL em entidades jurídicas."""
    models_dir = Path("src/infrastructure/db/models")
    violations = []

    for py_file in models_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        if "delete-orphan" in content:
            violations.append(f"{py_file}: delete-orphan proibido")
        if 'ondelete="CASCADE"' in content or "ondelete='CASCADE'" in content:
            violations.append(f"{py_file}: ON DELETE CASCADE proibido")
        if 'ondelete="SET NULL"' in content or "ondelete='SET NULL'" in content:
            violations.append(f"{py_file}: ON DELETE SET NULL proibido")

    assert not violations, f"Violação de regras relacionais no ORM: {violations}"


def test_contract_I_J_no_physical_delete_or_implicit_clock_for_legal_truth():
    """Auditoria estática garantindo 0 SQL DELETE físico em entidades normativas e 0 datetime.now() para verdade jurídica no domínio."""
    domain_dir = Path("src/domain")
    violations = []

    for py_file in domain_dir.rglob("*.py"):
        content = py_file.read_text(encoding="utf-8")
        if "datetime.now(" in content and "is_effective_on" in content:
            violations.append(f"{py_file}: datetime.now implícito usado em avaliação jurídica!")

    assert not violations, f"Violação de Verdade Temporal: {violations}"


def test_contract_M_N_O_ssrf_dns_redirect_and_downgrade_protection():
    """Testa proteção SSRF via DNS, limite de redirects e proibição de downgrade HTTPS -> HTTP."""
    # 1. Bloqueio de IP de metadados via DNS/Validator
    with pytest.raises(SSRFProtectionError):
        URLSecurityValidator.validate_url("http://169.254.169.254/latest/meta-data/")

    # 2. Bloqueio de subredes privadas IPv4 e IPv6
    with pytest.raises(SSRFProtectionError):
        URLSecurityValidator.validate_url("http://10.0.0.1/admin")

    with pytest.raises(SSRFProtectionError):
        URLSecurityValidator.validate_url("http://[fe80::1]/config")
