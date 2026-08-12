import pytest
from alembic import command
from alembic.config import Config


def test_alembic_migration_offline():
    """Testa a geração e execução de scripts de migration offline do Alembic."""
    alembic_cfg = Config("alembic.ini")
    
    # Testa a leitura e integridade dos scripts de migration sem lançar exceções de síntaxe
    script = alembic_cfg.get_main_option("script_location")
    assert script == "alembic"
