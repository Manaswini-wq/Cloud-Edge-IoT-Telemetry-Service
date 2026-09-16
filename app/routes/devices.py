"""
Device registration and management endpoints.
"""
from fastapi import APIRouter, Request, HTTPException, Depends, status
from datetime import datetime, timezone

from app.models.device_data import DeviceRegister, DeviceResponse
from app.middleware.auth import verify_api_key

router = APIRouter(tags=["devices"], dependencies=[Depends(verify_api_key)])


@router.post("/devices", response_model=DeviceResponse,
             status_code=status.HTTP_201_CREATED)
async def register_device(device: DeviceRegister, request: Request):
    """Register a new IoT device."""
    db = request.app.state.db

    if db.devices.find_one({"device_id": device.device_id}):
        raise HTTPException(status_code=409, detail="Device already registered")

    doc = {
        "device_id": device.device_id,
        "device_type": device.device_type,
        "location": device.location,
        "metadata": device.metadata or {},
        "registered_at": datetime.now(timezone.utc),
        "last_seen": None,
    }
    db.devices.insert_one(doc)
    return DeviceResponse(**doc)


@router.get("/devices/{device_id}", response_model=DeviceResponse)
async def get_device(device_id: str, request: Request):
    """Get device details."""
    doc = request.app.state.db.devices.find_one({"device_id": device_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Device not found")
    return DeviceResponse(**doc)


@router.get("/devices", response_model=list[DeviceResponse])
async def list_devices(request: Request):
    """List all registered devices."""
    docs = request.app.state.db.devices.find().sort("registered_at", -1).limit(100)
    return [DeviceResponse(**doc) for doc in docs]


@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(device_id: str, request: Request):
    """Unregister a device and delete its telemetry data."""
    db = request.app.state.db
    result = db.devices.delete_one({"device_id": device_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")
    db.telemetry.delete_many({"device_id": device_id})
