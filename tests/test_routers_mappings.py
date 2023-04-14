import pytest
import requests
from requests.exceptions import ConnectionError


@pytest.fixture(scope="session")
def api_service(docker_ip, docker_services) -> str:
    """Ensure that SSSOM API service is up and responsive."""

    api_port = docker_services.port_for("api", 8000)
    api_url = f"http://{docker_ip}:{api_port}/ui"
    triplestore_port = docker_services.port_for("triplestore", 8080)
    triplestore_url = f"http://{docker_ip}:{triplestore_port}/rdf4j-workbench"
    docker_services.wait_until_responsive(
        timeout=120,
        pause=0.1,
        check=lambda: is_responsive(f"{triplestore_url}/repositories/sssom/repositories")
    )
    return api_url


def is_responsive(service) -> bool:  # type: ignore
    try:
        response = requests.get(service)
        if response.status_code == 200:
            return True
    except ConnectionError:
        return False


def test_get_single_mapping(api_service: str):
    id = "38995e842357535cb5907261476d0174"
    response = requests.get(f"{api_service}/mappings/{id}")
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "mapping_justification": "https://w3id.org/semapv/ManualMappingCuration",
        "mapping_date": "2021-05-27",
        "subject_id": "http://purl.obolibrary.org/obo/MP_0000001",
        "comment": "KidsFirst; the best you could do is the MP root term that covers all phenotypes both normal and abnormal",
        "confidence": 1,
        "predicate_id": "http://www.w3.org/2004/02/skos/core#narrowMatch",
        "subject_label": "mammalian phenotype",
        "uuid": "38995e842357535cb5907261476d0174",
        "object_id": "http://purl.obolibrary.org/obo/HP_0000118",
        "object_label": "Phenotypic abnormality",
        "author_id": [
            "https://orcid.org/0000-0002-6490-7723",
            "https://orcid.org/0000-0003-4606-0597",
        ],
        "subject_id_curie": "MP:0000001",
        "object_id_curie": "HP:0000118",
    }
