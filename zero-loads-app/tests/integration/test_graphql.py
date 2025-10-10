import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient, ASGITransport

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
                            values: "headstay-load"
                            case: {
                                sails: ["full-mizzen-sail", "full-main-sail", "main-blade", "mizzen-jib"]
                                pcsMode: {aft: regeneration, fwd: propulsion}
                                awa: 0
                                aws: 25
                                seaState: wet
                            }
                        )
                        {
                            ranges {
                                errorTooHigh
                                errorTooLow
                                warningTooHigh
                                warningTooLow
                            }
                            target {
                                target
                                unit
                            }
                            value {
                                id
                                name
                            }
                            masts {
                                id
                                name
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
                            "ranges": {
                                "errorTooHigh": None,
                                "errorTooLow": None,
                                "warningTooHigh": None,
                                "warningTooLow": None,
                            },
                            "target": {"target": "5.0", "unit": "tonne"},
                            "value": {"id": "headstay-load", "name": "Headstay load"},
                            "masts": {"id": "main", "name": "Main mast"},
                        },
                        {
                            "ranges": {
                                "errorTooHigh": None,
                                "errorTooLow": None,
                                "warningTooHigh": None,
                                "warningTooLow": None,
                            },
                            "target": {"target": "2.5", "unit": "tonne"},
                            "value": {"id": "headstay-load", "name": "Headstay load"},
                            "masts": {"id": "mizzen", "name": "Mizzen mast"},
                        },
                    ]
                }
            }
