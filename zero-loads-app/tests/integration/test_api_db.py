import pytest
from sqlalchemy import inspect

from loads.api.schema import Base
from loads.config import Settings


@pytest.mark.asyncio
async def test_declarative_base_matches_db(settings: Settings, sessionmanager):
    async with sessionmanager.connect() as conn:
        schema = "loads"

        def get_db_objects_and_columns(sync_conn, schema=schema):
            inspector = inspect(sync_conn)
            db_tables = set(inspector.get_table_names(schema=schema))
            db_views = set(inspector.get_view_names(schema=schema))
            db_objects = db_tables | db_views

            db_columns = {
                t: {col["name"] for col in inspector.get_columns(t, schema=schema)}
                for t in db_objects
            }

            db_objects = {f"{schema}.{t}" for t in db_objects}
            db_columns = {f"{schema}.{t}": cols for t, cols in db_columns.items()}
            return db_objects, db_columns

        # The inspector is not available for async, so we use run_sync to get a synchronous connection.
        # https://getdocs.org/Sqlalchemy/docs/latest/orm/extensions/asyncio#Using_the_Inspector_to_inspect_schema_objects
        db_objects, db_columns = await conn.run_sync(get_db_objects_and_columns)
        model_tables = set(Base.metadata.tables.keys())
        assert model_tables <= db_objects, (
            f"Missing tables: {model_tables - db_objects}"
        )
        for table in model_tables:
            model_cols = set(Base.metadata.tables[table].columns.keys())
            assert model_cols == db_columns[table], (
                f"Column mismatch {table}: {model_cols} != {db_columns[table]}"
            )
