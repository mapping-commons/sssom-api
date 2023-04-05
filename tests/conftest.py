from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from src.main import create_app

@pytest.fixture
def app():
    return create_app()

@pytest.fixture
def client(app) -> TestClient:
    return TestClient(app)