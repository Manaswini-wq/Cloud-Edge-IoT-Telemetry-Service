"""
Entry point — creates the FastAPI application and registers routes.
"""
from fastapi import FastAPI
from pymongo import MongoClient
from contextlib import asynccontextmanager

from config import Config
from app.routes.devices import router as devices_router
from app.routes.telemetry import router as telemetry_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Connect to MongoDB on startup, close on shutdown."""
    client = MongoClient(Config.MONGO_URI)
    application.state.db = client[Config.MONGO_DB]

    # Create indexes for query performance
    application.state.db.telemetry.create_index(
        [("device_id", 1), ("timestamp", -1)]
    )
    application.state.db.telemetry.create_index([("timestamp", -1)])
    application.state.db.devices.create_index("device_id", unique=True)

    yield

    client.close()


def create_app() -> FastAPI:
    application = FastAPI(
        title="IoT Telemetry Service",
        description="Cloud-edge service for device telemetry ingestion and analytics",
        version="1.0.0",
        lifespan=lifespan,
    )
    application.include_router(devices_router, prefix="/api/v1")
    application.include_router(telemetry_router, prefix="/api/v1")
    return application


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
