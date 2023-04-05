from fastapi.testclient import TestClient

def test_get_single_mapping(client: TestClient):
    id = "8c835ed637ab5d11a29d088080f10114"
    response = client.get(f"/mappings/{id}")
    assert response.status_code == 200
    body = response.json()
    assert body == {
        ""
    }
    