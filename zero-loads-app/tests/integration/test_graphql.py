from fastapi.testclient import TestClient
from loads.api import app


def test_graphql():
    client = TestClient(app)
    response = client.post(
        "/graphql",
        json={
            "query": """
            query {
              referenceValues(
                values: "headstay-load"
                case: {
                  sails: ["full-mizzen-sail", "full-main-sail", "main-blade", "mizzen-jib"]
                  pcsMode: {aft: REGENERATION, fwd: PROPULSION}
                  awa: 0
                  aws: 25
                  seaState: WET
                }
              ) {
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
                    "target": {"target": "5.0", "unit": "TONNE"},
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
                    "target": {"target": "2.5", "unit": "TONNE"},
                    "value": {"id": "headstay-load", "name": "Headstay load"},
                    "masts": {"id": "mizzen", "name": "Mizzen mast"},
                },
            ]
        }
    }
