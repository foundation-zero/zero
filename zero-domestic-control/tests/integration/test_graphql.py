from fastapi.testclient import TestClient


def test_version(test_app):
    client = TestClient(test_app)
    response = client.post("/graphql", json={"query": "query { version }"})

    assert response.status_code == 200
    assert response.json() == {"data": {"version": "1.0.0"}}
