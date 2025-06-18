# Bussikartta

**Bussikartta** is a real-time public transport tracking system for the Helsinki region (HSL). It ingests live vehicle positions, compares them to scheduled GTFS data, and presents vehicle status on an interactive map.

---

## 🚀 System Overview

Bussikartta supports real-time monitoring and analytics of public transit by:

- Ingesting live data from HSL’s MQTT HFP feeds.
- Storing and querying recent vehicle positions via TimescaleDB.
- Periodically syncing static GTFS schedule data.
- Exposing a backend API for vehicle queries.
- Rendering real-time maps in a responsive frontend.

---

## 📦 Service Architecture

### 🖥️ Backend Services

| Service         | Description                                      | DB Tables Used       | Input Source       |
|-----------------|--------------------------------------------------|----------------------|--------------------|
| `mqtt-ingest`   | Realtime subscriber to MQTT HFP feeds           | `mqtt_hfp`           | MQTT feed (HSL)    |
| `vehicle-ingest`| Periodic GTFS-RT vehicle position fetch         | `vehicle_positions`  | GTFS-RT URL        |
| `gtfs-static`   | Loads static GTFS (routes, stops, trips)        | `routes`, `stops`, `trips`, etc. | GTFS ZIP |
| `api-server`    | FastAPI REST API server                         | read-only            | -                  |
| `backup`        | Snapshot script for TimescaleDB volumes         | file-level           | -                  |

### 🌐 Frontend

| Component       | Description                                | Stack                    |
|-----------------|--------------------------------------------|--------------------------|
| `MapView.tsx`   | Displays OpenStreetMap + markers (disabled) | React, MapLibre, Tailwind|
| `App.tsx`       | Polls vehicle API and logs updates          | React                    |

---

## 🗺️ Live Map

Currently displays a full-coverage street map using MapLibre. Vehicle markers are disabled for testing/debugging but API polling and console logging are active.

---

## 🧭 GTFS Data Handling

| Feature                     | Status |
|----------------------------|--------|
| Static GTFS ZIP fetch      | ✅     |
| Routes, Stops, Trips load  | ✅     |
| Vehicle position matching  | ✅     |
| Delay computation          | planned|
| Feed refresh/rotation      | planned|

---

## 📂 Repository Structure

| Path                | Purpose                                       |
|---------------------|-----------------------------------------------|
| `backend/`          | FastAPI API and ingestion orchestrators       |
| `frontend/`         | React app with map and polling UI             |
| `gtfs_static/`      | GTFS static ZIP fetcher and loader            |
| `ingestion/`        | MQTT and GTFS-RT handlers                     |
| `docs/`             | Developer and architecture docs               |
| `docker-compose.yaml` | Multi-service orchestration                |
| `backup.sh`         | TimescaleDB dump utility                      |

---

## 🧱 AI-Led Development Workflow

This project is fully AI-led and uses a strict shell + editor execution pattern:

- AI outputs full file replacements.
- Only `vi` and `BBEdit` are allowed for edits.
- Docker-compose service restart logic is included with changes.
- Logging is enabled across backend, frontend, MQTT and browser console.
- Development tracked via Active Task + Temporary Task switching.

See [docs/AI-Guidelines.md](docs/AI-Guidelines.md) for full protocol.

---

## 🧪 Quickstart

```bash
git clone https://github.com/skuduu/Bussikartta.git
cd Bussikartta
cp .env.example .env
docker compose up -d --build
docker compose exec api-server python scripts/import_gtfs.py
```

Access:
- Backend: [http://localhost:8000/docs](http://localhost:8000/docs)
- Frontend: [http://localhost:3000](http://localhost:3000)

---

## 📄 Documentation

- [Overview](docs/overview.md)
- [Project Architecture](docs/project_architecture.md)
- [GTFS Data Handling](docs/gtfs_data_handling.md)
- [Frontend Architecture](docs/frontend_architecture.md)
- [AI Development Rules](docs/AI-Guidelines.md)

---

*Bussikartta transforms open data into real-time insights for developers and commuters alike.*
