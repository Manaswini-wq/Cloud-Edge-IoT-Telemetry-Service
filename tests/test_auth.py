"""
Tests for API key authentication.
"""


def test_missing_api_key(client):
    resp = client.get("/api/v1/devices")
    assert resp.status_code == 401


def test_wrong_api_key(client):
    resp = client.get("/api/v1/devices", headers={"X-API-Key": "wrong-key"})
    assert resp.status_code == 401


def test_valid_api_key(client, auth_headers):
    resp = client.get("/api/v1/devices", headers=auth_headers)
    assert resp.status_code == 200
