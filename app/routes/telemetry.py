"""
Telemetry ingestion and query endpoints.
"""
from fastapi import APIRouter, Request, HTTPException, Depends, Query
from datetime import datetime, timezone
from typing import Optional

from app.models.device_data import (
    TelemetryPayload, TelemetryBatch, AggregationResult
)
from app.services.telemetry_service import TelemetryService
from app.services.analytics_service import AnalyticsService
from app.middleware.auth import verify_api_key

router = APIRouter(tags=["telemetry"], dependencies=[Depends(verify_api_key)])


@router.post("/telemetry", status_code=201)
async def ingest_single(payload: TelemetryPayload, request: Request):
    """Ingest a single telemetry data point."""
    svc = TelemetryService(request.app.state.db)
    result = svc.ingest(payload)
    return {"status": "ok", "inserted": 1, "id": str(result)}


@router.post("/telemetry/batch", status_code=201)
async def ingest_batch(batch: TelemetryBatch, request: Request):
    """Ingest a batch of telemetry data points (max 500)."""
    svc = TelemetryService(request.app.state.db)
    count = svc.ingest_batch(batch.data)
    return {"status": "ok", "inserted": count}


@router.get("/telemetry/{device_id}")
async def query_telemetry(
    device_id: str,
    request: Request,
    metric: Optional[str] = Query(None, description="Filter by metric name"),
    start: Optional[datetime] = Query(None, description="Start time (ISO 8601)"),
    end: Optional[datetime] = Query(None, description="End time (ISO 8601)"),
    limit: int = Query(100, ge=1, le=1000),
):
    """Query telemetry data for a device."""
    svc = TelemetryService(request.app.state.db)
    results = svc.query(device_id, metric=metric, start_time=start,
                        end_time=end, limit=limit)
    return {"device_id": device_id, "count": len(results), "data": results}


@router.get("/telemetry/{device_id}/latest")
async def get_latest(device_id: str, request: Request):
    """Get the most recent telemetry reading for a device."""
    svc = TelemetryService(request.app.state.db)
    result = svc.get_latest(device_id)
    if not result:
        raise HTTPException(status_code=404, detail="No telemetry data found")
    return result


@router.get("/analytics/{device_id}", response_model=list[AggregationResult])
async def get_analytics(
    device_id: str,
    request: Request,
    metric: str = Query(..., description="Metric name to aggregate"),
    window: str = Query("1h", description="Aggregation window: 1m, 5m, 1h, 1d"),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
):
    """Get aggregated analytics (avg/min/max) for a device metric."""
    svc = AnalyticsService(request.app.state.db)
    results = svc.aggregate(device_id, metric, window, start_time=start,
                            end_time=end)
    return results
