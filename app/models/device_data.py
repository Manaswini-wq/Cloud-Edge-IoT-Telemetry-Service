"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DeviceRegister(BaseModel):
    """Register a new IoT device."""
    device_id: str = Field(..., min_length=1, max_length=64,
                           examples=["sensor-hub-001"])
    device_type: str = Field(..., examples=["temperature_sensor"])
    location: Optional[str] = Field(None, examples=["building-A-floor-2"])
    metadata: Optional[dict] = None


class DeviceResponse(BaseModel):
    device_id: str
    device_type: str
    location: Optional[str]
    registered_at: datetime
    last_seen: Optional[datetime]


class TelemetryPayload(BaseModel):
    """Single telemetry data point from a device."""
    device_id: str = Field(..., min_length=1)
    timestamp: Optional[datetime] = None
    metrics: dict = Field(..., examples=[{
        "temperature_c": 23.5,
        "humidity_pct": 45.2,
        "pressure_pa": 101325
    }])


class TelemetryBatch(BaseModel):
    """Batch of telemetry data points."""
    data: list[TelemetryPayload] = Field(..., min_length=1, max_length=500)


class TelemetryQuery(BaseModel):
    device_id: Optional[str] = None
    metric: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)


class AggregationResult(BaseModel):
    device_id: str
    metric: str
    window: str
    avg: float
    min: float
    max: float
    count: int
    start_time: datetime
    end_time: datetime
