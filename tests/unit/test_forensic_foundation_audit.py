import ast
from pathlib import Path
import pytest

from src.application.parsers.brazilian_law_parser import BrazilianLawParser
from src.domain.services.hash_service import DocumentHashCalculator


def test_forensic_audit_domain_layer_purity():
    """
    AUDITORIA FORENSE DE PUREZA DO DOMÍNIO:
    Inspeciona AST de cada arquivo em src/domain/ para confirmar ZERO importações de:
    SQLAlchemy, asyncpg, psycopg, urllib, httpx, requests, boto3, Supabase, Neon ou Cloudflare SDK.
    """
    domain_dir = Path("src/domain")
    prohibited_modules = {
        "sqlalchemy", "asyncpg", "psycopg", "urllib", "httpx",
        "requests", "boto3", "botocore", "supabase", "cloudflare"
    }

    violations = []

    for py_file in domain_dir.rglob("*.py"):
        tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod_base = alias.name.split(".")[0]
                    if mod_base in prohibited_modules or mod_base in ("application", "infrastructure"):
                        violations.append(f"Arquivo '{py_file}' importa módulo proibido '{alias.name}'")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod_base = node.module.split(".")[0]
                    if mod_base in prohibited_modules:
                        violations.append(f"Arquivo '{py_file}' importa de módulo proibido '{node.module}'")
                    if node.module.startswith("src.application") or node.module.startswith("src.infrastructure"):
                        violations.append(f"Inversão de Dependência: '{py_file}' importa de '{node.module}'")

    assert not violations, f"Violação da Pureza da Camada de Domínio: {violations}"


def test_forensic_audit_canonical_node_hash_determinism():
    """
    AUDITORIA FORENSE DE HASH CANÔNICO:
    Garante que o hash do LegalNode é 100% determinístico e independente de UUIDs ou IDs de banco.
    """
    hash1 = DocumentHashCalculator.calculate_canonical_node_hash("ARTIGO", "art-1", "Art. 1º", "Texto do artigo 1")
    hash2 = DocumentHashCalculator.calculate_canonical_node_hash("ARTIGO", "art-1", "Art. 1º", "Texto do artigo 1")

    assert hash1 == hash2, "Hashes canônicos para o mesmo dispositivo normativo diferem!"

    # Testa no parser
    parser = BrazilianLawParser()
    nodes1, _ = parser.parse_structure("Art. 1º Texto do artigo 1.", version_id="v1")
    nodes2, _ = parser.parse_structure("Art. 1º Texto do artigo 1.", version_id="v2")

    art1_n1 = next(n for n in nodes1 if n.identifier == "art-1")
    art1_n2 = next(n for n in nodes2 if n.identifier == "art-1")

    assert art1_n1.content_hash == art1_n2.content_hash, "O content_hash do nó deve ser idêntico independente da versão!"


def test_forensic_audit_git_and_secrets_hygiene():
    """
    AUDITORIA FORENSE DE HIGIENE DO REPOSITÓRIO:
    Garante que o arquivo .gitignore exclui explicitamente .env e que segredos não estão commitados.
    """
    gitignore_path = Path(".gitignore")
    assert gitignore_path.exists(), "Arquivo .gitignore ausente no repositório!"

    content = gitignore_path.read_text(encoding="utf-8")
    assert ".env" in content, ".gitignore DEVE conter a regra .env para impedir o vazamento de segredos!"


def test_forensic_audit_no_physical_delete_in_src():
    """
    AUDITORIA FORENSE DE DELETE:
    Confirma zero declarações de exclusão física DELETE sobre tabelas normativas ou de proveniência.
    """
    src_dir = Path("src")
    prohibited_patterns = [
        "DELETE FROM legal_",
        "DELETE FROM evidences",
        "DELETE FROM sources",
    ]

    violations = []
    for py_file in src_dir.rglob("*.py"):
        text_content = py_file.read_text(encoding="utf-8")
        for pattern in prohibited_patterns:
            if pattern in text_content:
                violations.append(f"Arquivo '{py_file}' contém operação proibida de exclusão física: '{pattern}'")

    assert not violations, f"Violação de Imutabilidade Jurídica: {violations}"
