"""
Tests for Pydantic model validation.
"""
import pytest
from pydantic import ValidationError
from app.models.device_data import DeviceRegister, TelemetryPayload, TelemetryBatch


def test_device_register_valid():
    d = DeviceRegister(device_id="sensor-1", device_type="temp")
    assert d.device_id == "sensor-1"


def test_device_register_empty_id():
    with pytest.raises(ValidationError):
        DeviceRegister(device_id="", device_type="temp")


def test_telemetry_payload_valid():
    p = TelemetryPayload(device_id="s1", metrics={"temp": 25.0})
    assert p.metrics["temp"] == 25.0
    assert p.timestamp is None  # auto-filled at ingestion


def test_telemetry_batch_max_size():
    with pytest.raises(ValidationError):
        TelemetryBatch(data=[
            TelemetryPayload(device_id="s1", metrics={"t": i})
            for i in range(501)  # exceeds max 500
        ])


def test_telemetry_batch_empty():
    with pytest.raises(ValidationError):
        TelemetryBatch(data=[])
