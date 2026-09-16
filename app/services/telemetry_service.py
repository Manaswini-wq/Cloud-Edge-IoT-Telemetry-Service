"""
Core telemetry business logic — ingestion, querying, validation.
"""
from datetime import datetime, timezone
from typing import Optional

from app.models.device_data import TelemetryPayload


class TelemetryService:
    def __init__(self, db):
        self.db = db
        self.collection = db.telemetry
        self.devices = db.devices

    def ingest(self, payload: TelemetryPayload) -> str:
        """Ingest a single telemetry data point. Returns inserted document ID."""
        doc = self._build_document(payload)
        result = self.collection.insert_one(doc)

        # Update device last_seen timestamp
        self.devices.update_one(
            {"device_id": payload.device_id},
            {"$set": {"last_seen": doc["timestamp"]}},
        )
        return result.inserted_id

    def ingest_batch(self, payloads: list[TelemetryPayload]) -> int:
        """Ingest multiple data points. Returns count of inserted documents."""
        if not payloads:
            return 0

        docs = [self._build_document(p) for p in payloads]
        result = self.collection.insert_many(docs)

        # Bulk update last_seen for all devices in batch
        device_timestamps = {}
        for doc in docs:
            did = doc["device_id"]
            ts = doc["timestamp"]
            if did not in device_timestamps or ts > device_timestamps[did]:
                device_timestamps[did] = ts

        for did, ts in device_timestamps.items():
            self.devices.update_one(
                {"device_id": did},
                {"$set": {"last_seen": ts}},
            )
        return len(result.inserted_ids)

    def query(self, device_id: str, metric: Optional[str] = None,
              start_time: Optional[datetime] = None,
              end_time: Optional[datetime] = None,
              limit: int = 100) -> list[dict]:
        """Query telemetry data with optional filters."""
        query_filter = {"device_id": device_id}

        if start_time or end_time:
            query_filter["timestamp"] = {}
            if start_time:
                query_filter["timestamp"]["$gte"] = start_time
            if end_time:
                query_filter["timestamp"]["$lte"] = end_time

        if metric:
            query_filter[f"metrics.{metric}"] = {"$exists": True}

        cursor = (self.collection
                  .find(query_filter, {"_id": 0})
                  .sort("timestamp", -1)
                  .limit(limit))

        results = list(cursor)
        if metric:
            for r in results:
                r["value"] = r["metrics"].get(metric)
        return results

    def get_latest(self, device_id: str) -> Optional[dict]:
        """Get the most recent telemetry reading."""
        doc = (self.collection
               .find_one({"device_id": device_id},
                         {"_id": 0},
                         sort=[("timestamp", -1)]))
        return doc

    def _build_document(self, payload: TelemetryPayload) -> dict:
        return {
            "device_id": payload.device_id,
            "timestamp": payload.timestamp or datetime.now(timezone.utc),
            "metrics": payload.metrics,
        }
