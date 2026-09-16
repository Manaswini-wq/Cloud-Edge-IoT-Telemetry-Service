"""
Analytics service — MongoDB aggregation pipelines for time-series analysis.
"""
from datetime import datetime, timezone, timedelta
from typing import Optional

from app.models.device_data import AggregationResult


WINDOW_SECONDS = {
    "1m": 60,
    "5m": 300,
    "1h": 3600,
    "1d": 86400,
}


class AnalyticsService:
    def __init__(self, db):
        self.db = db
        self.collection = db.telemetry

    def aggregate(self, device_id: str, metric: str, window: str = "1h",
                  start_time: Optional[datetime] = None,
                  end_time: Optional[datetime] = None) -> list[AggregationResult]:
        """
        Run a time-bucketed aggregation (avg/min/max/count) using
        MongoDB's $group pipeline stage.
        """
        if window not in WINDOW_SECONDS:
            raise ValueError(f"Invalid window. Must be one of: {list(WINDOW_SECONDS)}")

        window_secs = WINDOW_SECONDS[window]

        if not end_time:
            end_time = datetime.now(timezone.utc)
        if not start_time:
            start_time = end_time - timedelta(hours=24)

        metric_field = f"$metrics.{metric}"

        pipeline = [
            {
                "$match": {
                    "device_id": device_id,
                    "timestamp": {"$gte": start_time, "$lte": end_time},
                    f"metrics.{metric}": {"$exists": True},
                }
            },
            {
                "$group": {
                    "_id": {
                        "bucket": {
                            "$subtract": [
                                {"$toLong": "$timestamp"},
                                {"$mod": [{"$toLong": "$timestamp"}, window_secs * 1000]}
                            ]
                        }
                    },
                    "avg": {"$avg": metric_field},
                    "min": {"$min": metric_field},
                    "max": {"$max": metric_field},
                    "count": {"$sum": 1},
                    "start_time": {"$min": "$timestamp"},
                    "end_time": {"$max": "$timestamp"},
                }
            },
            {"$sort": {"_id.bucket": 1}},
        ]

        results = []
        for doc in self.collection.aggregate(pipeline):
            results.append(AggregationResult(
                device_id=device_id,
                metric=metric,
                window=window,
                avg=round(doc["avg"], 4),
                min=round(doc["min"], 4),
                max=round(doc["max"], 4),
                count=doc["count"],
                start_time=doc["start_time"],
                end_time=doc["end_time"],
            ))
        return results
