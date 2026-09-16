"""
Database initialization script — creates collections, indexes, and seed data.
Run once: python -m migrations.init_db
"""
from pymongo import MongoClient, ASCENDING, DESCENDING
from config import Config


def init_database():
    client = MongoClient(Config.MONGO_URI)
    db = client[Config.MONGO_DB]

    # Create collections with schema validation
    if "devices" not in db.list_collection_names():
        db.create_collection("devices")
    if "telemetry" not in db.list_collection_names():
        db.create_collection("telemetry")

    # Indexes for query performance
    db.devices.create_index("device_id", unique=True)
    db.telemetry.create_index([("device_id", ASCENDING), ("timestamp", DESCENDING)])
    db.telemetry.create_index([("timestamp", DESCENDING)])

    # TTL index — auto-delete telemetry older than 90 days
    db.telemetry.create_index("timestamp", expireAfterSeconds=90 * 86400)

    print("Database initialized:")
    print(f"  URI: {Config.MONGO_URI}")
    print(f"  DB:  {Config.MONGO_DB}")
    print(f"  Collections: {db.list_collection_names()}")
    print(f"  Indexes: {db.telemetry.index_information()}")

    client.close()


if __name__ == "__main__":
    init_database()
