"""
Application configuration — loaded from environment variables with sensible defaults.
"""
import os


class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB = os.getenv("MONGO_DB", "iot_telemetry")
    API_KEY = os.getenv("API_KEY", "dev-api-key-change-in-production")
    MAX_QUERY_LIMIT = 1000
    DEFAULT_QUERY_LIMIT = 100
    AGGREGATION_WINDOWS = ["1m", "5m", "1h", "1d"]
