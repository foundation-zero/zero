from fastapi.testclient import TestClient
from zero_domestic_control.app import app


def test_version():
    client = TestClient(app)
    response = client.post("/graphql", json={"query": "query { version }"})

    assert response.status_code == 200
    assert response.json() == {"data": {"version": "1.0.0"}}
