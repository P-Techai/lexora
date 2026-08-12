import os
import pytest
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

TEST_DB_URL = os.getenv("TEST_DATABASE_URL")


def test_alembic_migration_script_chain_integrity():
    """Testa a leitura e integridade da cadeia de scripts de migration (0001 -> 0002 -> 0003 -> 0004)."""
    alembic_cfg = Config("alembic.ini")
    script_dir = ScriptDirectory.from_config(alembic_cfg)
    
    revisions = [s.revision for s in script_dir.walk_revisions()]
    
    assert "0001_canonical_legal_model" in revisions
    assert "0002_acquisition_and_artifacts" in revisions
    assert "0003_legal_integrity_hardening" in revisions
    assert "0004_evidence_fk_integrity" in revisions

    head_rev = script_dir.get_current_head()
    assert head_rev == "0004_evidence_fk_integrity"


def test_alembic_round_trip_upgrade_downgrade_on_database():
    """
    TESTE DE ROUND-TRIP DE MIGRATIONS:
    Executa: upgrade 0004 -> downgrade 0003 -> upgrade 0004.
    Requer TEST_DATABASE_URL ou banco configurado.
    """
    if not TEST_DB_URL:
        pytest.skip("TEST_DATABASE_URL não configurada: Teste de round-trip de migration ignorado por ausência de DB relacional.")

    sync_url = TEST_DB_URL.replace("+asyncpg", "")
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", sync_url)

    # 1. Upgrade para head (0004)
    command.upgrade(alembic_cfg, "head")

    # 2. Downgrade para 0003
    command.downgrade(alembic_cfg, "0003_legal_integrity_hardening")

    # 3. Re-upgrade para head (0004)
    command.upgrade(alembic_cfg, "head")
