"""
Tests for telemetry ingestion and query endpoints.
"""


def test_ingest_single(client, auth_headers, registered_device):
    payload = {
        "device_id": "test-sensor-001",
        "metrics": {"temperature_c": 23.5, "humidity_pct": 45.0},
    }
    resp = client.post("/api/v1/telemetry", json=payload, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["inserted"] == 1


def test_ingest_batch(client, auth_headers, registered_device):
    batch = {
        "data": [
            {"device_id": "test-sensor-001",
             "metrics": {"temperature_c": 22.0 + i}}
            for i in range(10)
        ]
    }
    resp = client.post("/api/v1/telemetry/batch", json=batch, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["inserted"] == 10


def test_query_telemetry(client, auth_headers, registered_device):
    # Ingest data first
    for temp in [20.0, 21.0, 22.0]:
        client.post("/api/v1/telemetry", json={
            "device_id": "test-sensor-001",
            "metrics": {"temperature_c": temp},
        }, headers=auth_headers)

    resp = client.get("/api/v1/telemetry/test-sensor-001", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["count"] == 3


def test_query_with_metric_filter(client, auth_headers, registered_device):
    client.post("/api/v1/telemetry", json={
        "device_id": "test-sensor-001",
        "metrics": {"temperature_c": 25.0, "humidity_pct": 50.0},
    }, headers=auth_headers)

    resp = client.get(
        "/api/v1/telemetry/test-sensor-001?metric=temperature_c",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["data"][0]["value"] == 25.0


def test_get_latest(client, auth_headers, registered_device):
    for temp in [20.0, 25.0, 30.0]:
        client.post("/api/v1/telemetry", json={
            "device_id": "test-sensor-001",
            "metrics": {"temperature_c": temp},
        }, headers=auth_headers)

    resp = client.get("/api/v1/telemetry/test-sensor-001/latest",
                      headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["metrics"]["temperature_c"] == 30.0


def test_latest_not_found(client, auth_headers):
    resp = client.get("/api/v1/telemetry/nonexistent/latest",
                      headers=auth_headers)
    assert resp.status_code == 404


def test_ingest_updates_last_seen(client, auth_headers, registered_device):
    client.post("/api/v1/telemetry", json={
        "device_id": "test-sensor-001",
        "metrics": {"temperature_c": 25.0},
    }, headers=auth_headers)

    resp = client.get("/api/v1/devices/test-sensor-001", headers=auth_headers)
    assert resp.json()["last_seen"] is not None
