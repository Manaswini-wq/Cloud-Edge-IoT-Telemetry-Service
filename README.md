# IoT Telemetry Service

A cloud-edge backend service for IoT device telemetry ingestion, querying, and time-series analytics. Built with **FastAPI**, **MongoDB**, and **Docker**.

## Architecture

```
IoT Devices                    Cloud Service                    Database
┌──────────┐    REST API    ┌───────────────────┐           ┌──────────┐
│ Sensor   │───────────────>│  FastAPI App       │──────────>│ MongoDB  │
│ Hub      │  POST /telemetry│                   │  pymongo  │          │
│ (ESP32)  │<───────────────│  ┌──────────────┐  │<──────────│ telemetry│
└──────────┘  GET /analytics │  │ Routes       │  │  queries  │ devices  │
                             │  ├──────────────┤  │           └──────────┘
Dashboard                    │  │ Services     │  │
┌──────────┐  GET /telemetry │  ├──────────────┤  │
│ Grafana  │────────────────>│  │ Models       │  │
│ Web UI   │                 │  ├──────────────┤  │
└──────────┘                 │  │ Auth (API Key)│  │
                             │  └──────────────┘  │
                             └───────────────────┘
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/devices` | Register a new device |
| GET | `/api/v1/devices` | List all devices |
| GET | `/api/v1/devices/{id}` | Get device details |
| DELETE | `/api/v1/devices/{id}` | Unregister device |
| POST | `/api/v1/telemetry` | Ingest single data point |
| POST | `/api/v1/telemetry/batch` | Ingest batch (up to 500) |
| GET | `/api/v1/telemetry/{id}` | Query device telemetry |
| GET | `/api/v1/telemetry/{id}/latest` | Get latest reading |
| GET | `/api/v1/analytics/{id}` | Time-bucketed aggregation |

All endpoints require `X-API-Key` header for authentication.

## Quick Start

```bash
# Start MongoDB + API with Docker
docker-compose up -d

# Or run locally
pip install -r requirements.txt
python -m migrations.init_db
uvicorn app.main:app --reload

# Run tests
pytest -v
```

## Usage Examples

```bash
# Register a device
curl -X POST http://localhost:8000/api/v1/devices \
  -H "X-API-Key: my-secure-api-key" \
  -H "Content-Type: application/json" \
  -d '{"device_id": "sensor-001", "device_type": "temperature_sensor"}'

# Send telemetry
curl -X POST http://localhost:8000/api/v1/telemetry \
  -H "X-API-Key: my-secure-api-key" \
  -H "Content-Type: application/json" \
  -d '{"device_id": "sensor-001", "metrics": {"temperature_c": 23.5, "humidity_pct": 45.0}}'

# Query analytics (hourly avg/min/max)
curl "http://localhost:8000/api/v1/analytics/sensor-001?metric=temperature_c&window=1h" \
  -H "X-API-Key: my-secure-api-key"
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.12 |
| Framework | FastAPI |
| Database | MongoDB 7 |
| ORM/Driver | pymongo |
| Validation | Pydantic v2 |
| Auth | API Key (X-API-Key header) |
| Testing | pytest, httpx |
| Container | Docker, docker-compose |

## Design Decisions

1. **MongoDB over SQL** — Telemetry data is schema-flexible (different devices send different metrics). MongoDB's document model handles this naturally without ALTER TABLE.
2. **TTL Index** — Telemetry auto-deletes after 90 days via MongoDB TTL index. No cron job needed.
3. **Aggregation Pipeline** — Analytics use MongoDB's `$group` stage for time-bucketed stats, pushing computation to the database layer instead of Python.
4. **Batch Ingestion** — Devices can POST up to 500 data points in one request, reducing HTTP overhead for high-frequency sensors.
