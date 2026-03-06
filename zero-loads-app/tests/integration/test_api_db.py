import pytest
from sqlalchemy import inspect, select

from loads.api.schema import Base, ReferenceValues
from loads.config import Settings
from loads.registry import VARIABLES


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


@pytest.mark.asyncio
async def test_reference_values_variable_ids_in_registry(sessionmanager):
    """Test that all variable_ids in reference_values table exist in VARIABLES registry."""
    async with sessionmanager.session() as session:
        # Query all distinct variable_ids from the reference_values table
        query = select(ReferenceValues.variable_id).distinct()
        result = await session.execute(query)
        db_variable_ids = set(result.scalars().all())

        # Get all variable IDs from the registry
        registry_variable_ids = set(VARIABLES.keys())

        # Check that all variable_ids from the database are in the registry
        missing_variables = db_variable_ids - registry_variable_ids
        assert not missing_variables, (
            f"The following variable_ids from reference_values are not in VARIABLES registry: {missing_variables}"
        )
