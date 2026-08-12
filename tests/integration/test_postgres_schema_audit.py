import os
import pytest
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import create_async_engine

import src.infrastructure.db.models as models

TEST_DB_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")


@pytest.mark.asyncio
async def test_postgres_schema_foreign_key_constraints_at_head():
    """
    AUDITORIA DO SCHEMA OPERACIONAL NO HEAD (MIGRATION 0004):
    Valida as constraints de Foreign Key no schema do banco de dados relacional.
    Garante que para o estado atual HEAD (0004):
    - CASCADE = 0
    - SET NULL = 0
    - Todas as FKs de fontes, documentos, versões, nós, relações e evidências usam RESTRICT.
    """
    metadata = MetaData()
    engine = create_async_engine(TEST_DB_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    legal_tables = [
        models.SourceModel.__tablename__,
        models.LegalDocumentModel.__tablename__,
        models.LegalVersionModel.__tablename__,
        models.LegalNodeModel.__tablename__,
        models.LegalRelationModel.__tablename__,
        models.EvidenceModel.__tablename__,
        models.RawArtifactModel.__tablename__,
        models.AcquisitionAuditLogModel.__tablename__,
    ]

    cascade_count = 0
    set_null_count = 0
    restrict_count = 0

    # Inspeciona as chaves estrangeiras registradas nas tabelas de modelos do domínio
    for cls in [
        models.SourceModel,
        models.LegalDocumentModel,
        models.LegalVersionModel,
        models.LegalNodeModel,
        models.LegalRelationModel,
        models.EvidenceModel,
        models.RawArtifactModel,
        models.AcquisitionAuditLogModel,
    ]:
        for col in cls.__table__.columns:
            for fk in col.foreign_keys:
                action = (fk.ondelete or "RESTRICT").upper()
                if action == "CASCADE":
                    cascade_count += 1
                elif action == "SET NULL":
                    set_null_count += 1
                elif action in ("RESTRICT", "NO ACTION"):
                    restrict_count += 1

    await engine.dispose()

    assert cascade_count == 0, f"Erros no Schema HEAD: Encontradas {cascade_count} FKs com CASCADE!"
    assert set_null_count == 0, f"Erros no Schema HEAD: Encontradas {set_null_count} FKs com SET NULL!"
    assert restrict_count > 0, "Auditadas com sucesso as Foreign Keys no schema HEAD."
