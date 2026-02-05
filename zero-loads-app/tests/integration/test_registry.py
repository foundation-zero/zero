from sqlalchemy import select

from loads.api.db import SessionManager
from loads.api.schema import Variables
from loads.registry.registry import VARIABLES


async def test_all_variables_in_db(sessionmanager: SessionManager):
    async with sessionmanager.connect() as conn:
        query = (
            select(Variables.id).where(Variables.id.in_(VARIABLES.keys())).distinct()
        )

        result = await conn.execute(query)
        from_db = set(row[0] for row in result.fetchall())

        variable_ids = set(VARIABLES.keys())

        assert variable_ids == from_db
