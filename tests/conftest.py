"""
Pytest fixtures — spins up a test FastAPI client with a temporary MongoDB database.
"""
import pytest
from fastapi.testclient import TestClient
from pymongo import MongoClient

from app.main import create_app
from config import Config


@pytest.fixture(scope="session")
def mongo_client():
    client = MongoClient(Config.MONGO_URI)
    yield client
    client.close()


@pytest.fixture(autouse=True)
def test_db(mongo_client):
    """Fresh database for each test — drops after test completes."""
    db = mongo_client["iot_telemetry_test"]
    yield db
    mongo_client.drop_database("iot_telemetry_test")


@pytest.fixture
def client(test_db):
    """FastAPI test client with test database injected."""
    application = create_app()
    application.state.db = test_db
    with TestClient(application) as c:
        yield c


@pytest.fixture
def auth_headers():
    return {"X-API-Key": Config.API_KEY}


@pytest.fixture
def registered_device(client, auth_headers):
    """Pre-register a device for tests that need one."""
    device = {
        "device_id": "test-sensor-001",
        "device_type": "temperature_sensor",
        "location": "lab-bench-1",
    }
    client.post("/api/v1/devices", json=device, headers=auth_headers)
    return device
