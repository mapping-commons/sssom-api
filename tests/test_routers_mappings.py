from fastapi.testclient import TestClient


def test_get_single_mapping(client: TestClient):
    id = "8c835ed637ab5d11a29d088080f10114"
    response = client.get(f"/mappings/{id}")
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "subject_id": "http://purl.obolibrary.org/obo/MP_0001289",
        "predicate_id": "http://www.w3.org/2004/02/skos/core#closeMatch",
        "object_id": "http://purl.obolibrary.org/obo/HP_0007968",
        "mapping_justification": "https://w3id.org/semapv/LexicalMatching",
    }
