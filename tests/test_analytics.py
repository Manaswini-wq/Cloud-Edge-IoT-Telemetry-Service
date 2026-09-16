"""
Tests for analytics aggregation endpoints.
"""
from datetime import datetime, timezone, timedelta


def test_hourly_aggregation(client, auth_headers, registered_device):
    now = datetime.now(timezone.utc)
    for i in range(5):
        client.post("/api/v1/telemetry", json={
            "device_id": "test-sensor-001",
            "timestamp": (now - timedelta(minutes=i)).isoformat(),
            "metrics": {"temperature_c": 20.0 + i},
        }, headers=auth_headers)

    resp = client.get(
        "/api/v1/analytics/test-sensor-001?metric=temperature_c&window=1h",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert data[0]["count"] == 5
    assert data[0]["min"] == 20.0
    assert data[0]["max"] == 24.0


def test_no_data_returns_empty(client, auth_headers, registered_device):
    resp = client.get(
        "/api/v1/analytics/test-sensor-001?metric=temperature_c&window=1h",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json() == []
