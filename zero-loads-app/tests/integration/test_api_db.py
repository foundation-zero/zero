import pytest
from sqlalchemy import inspect
from loads.api.schema import Base
from loads.config import Settings


@pytest.mark.asyncio
async def test_declarative_base_matches_db(settings: Settings, sessionmanager):
    async with sessionmanager.connect() as conn:

        def get_db_tables_and_columns(sync_conn):
            inspector = inspect(sync_conn)
            db_tables = set(inspector.get_table_names())
            db_columns = {
                t: {col["name"] for col in inspector.get_columns(t)} for t in db_tables
            }
            return db_tables, db_columns

        db_tables, db_columns = await conn.run_sync(get_db_tables_and_columns)
        model_tables = set(Base.metadata.tables.keys()) - {"sail_sets_combined"}
        assert model_tables <= db_tables, f"Missing tables: {model_tables - db_tables}"
        for table in model_tables:
            model_cols = set(Base.metadata.tables[table].columns.keys())
            assert model_cols == db_columns[table], (
                f"Column mismatch {table}: {model_cols} != {db_columns[table]}"
            )
