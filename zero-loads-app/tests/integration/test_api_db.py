import pytest
from sqlalchemy import inspect
from backend.api.db import Base, engine


@pytest.mark.asyncio
async def test_declarative_base_matches_db():
    async with engine.begin() as conn:

        def get_db_tables_and_columns(sync_conn):
            inspector = inspect(sync_conn)
            db_tables = set(inspector.get_table_names())
            db_columns = {
                table_name: set(
                    col["name"] for col in inspector.get_columns(table_name)
                )
                for table_name in db_tables
            }
            return db_tables, db_columns

        db_tables, db_columns = await conn.run_sync(get_db_tables_and_columns)
        # sail_sets_combined is a view not a table.
        model_tables = set(Base.metadata.tables.keys()) - {"sail_sets_combined"}
        assert model_tables <= db_tables, (
            f"Missing tables in DB: {model_tables - db_tables}"
        )

        for table_name in model_tables:
            model_columns = set(Base.metadata.tables[table_name].columns.keys())
            assert model_columns == db_columns[table_name], (
                f"Column mismatch in table '{table_name}': "
                f"Expected {model_columns}, Found {db_columns[table_name]}"
            )
