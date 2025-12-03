import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from loads.api import app


@pytest.mark.asyncio
async def test_graphql():
    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app), base_url="http://test"
        ) as client:
            response = await client.post(
                "/graphql",
                json={
                    "query": """
                    query {
                        referenceValues(
                            case: {awa: 27, aws: 16, sailset: [full_main, full_mizzen, blade]}
                            variables: "main-sheet-load"
                        )
                        {
                    reference {
                        alarmLow
                        warningLow
                        target
                        warningHigh
                        alarmHigh
                        }
                    variable {
                        id
                        }
                    }
                }
                """
                },
            )

            assert response.status_code == 200
            assert response.json() == {
                "data": {
                    "referenceValues": [
                        {
                            "reference": {
                                "alarmLow": None,
                                "warningLow": None,
                                "target": None,
                                "warningHigh": None,
                                "alarmHigh": 15.0,
                            },
                            "variable": {"id": "main-sheet-load"},
                        }
                    ]
                }
            }
