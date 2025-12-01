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
            response = client.post(
                "/graphql",
                json={
                    "query": """
                    query {
                        referenceValues(
                            case: {twa: 45, tws: 16, sailset: [full_main, full_mizzen, blade]}
                            variables: "headstay-load"
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

            response = await response
            assert response.status_code == 200
            assert response.json() == {
                "data": {
                    "referenceValues": [
                        {
                            "reference": {
                                "alarmLow": None,
                                "warningLow": None,
                                "target": 10,
                                "warningHigh": None,
                                "alarmHigh": None,
                            },
                            "variable": {"id": "headstay-load"},
                        }
                    ]
                }
            }
