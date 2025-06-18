# Bussikartta Overview

## 1. Basic Overview

**Bussikartta** is a real-time transit tracking system designed for Helsinki Region Transport (HSL). It combines static schedule data with live vehicle telemetry to show real-time positions and delay information of buses on an interactive map.

### Key Functionalities

- **Static GTFS Schedule Import**: Imports routes, trips, stops, and timetables from HSL’s GTFS feed into a TimescaleDB database.
- **Live Data Ingestion**: Subscribes to HSL’s MQTT feed to receive live vehicle position updates and status events.
- **Delay Calculation**: Computes delays (ahead or behind schedule) by comparing live arrival times to scheduled times.
- **API for Clients**: Exposes REST endpoints via FastAPI for querying vehicles, delays, stops, and routes.
- **Interactive Frontend**: A React + MapLibre-based web app that displays bus positions and delays on an interactive map.
- **Containerized Setup**: Uses Docker Compose to orchestrate backend, frontend, and database services.

### Purpose

Enable developers and users to visualize live bus locations and delays in Helsinki, providing a backend-powered API and an easy-to-deploy interface.

---

## 2. Detailed Overview

### 🏛 Architecture

The system comprises several coordinated services:

```
[ GTFS Feed ] ─── import_gtfs.py ──► [TimescaleDB Static GTFS Tables]
                   ↑
                   └─────────────────┐
                                     ▼
                                FastAPI Backend ◄─────────────
                   ▲           (REST APIs, delay logic)        │
                   │                                             │
[ HSL MQTT        └─────────────────────────────────────────────►│
  Live Feed ]           MQTT Subscriber        Live Vehicle Data│
                                                         ▲     │
                                                         └─────┘
                                          React + MapLibre Frontend
```

### Core Components

#### 1. `gtfs_scheduler/` or `scripts/import_gtfs.py`
- Parses GTFS ZIP feed (CSV format).
- Populates static database tables: `routes`, `trips`, `stop_times`, `stops`, etc.
- Ensures the database reflects the latest official schedule.

#### 2. `mqtt_subscriber/` or integrated subscriber service
- Uses an MQTT client (e.g. Paho) to connect to the HSL MQTT broker.
- Subscribes to relevant topics (e.g. `HSL/HFP/...`).
- On message:
  - Parses vehicle ID, timestamp, lat/lon, stop info.
  - Inserts into realtime table and triggers delay calculation.

#### 3. `backend/` (FastAPI)
- Provides REST endpoints, including:
  - `/vehicles`: current vehicle positions and meta info.
  - `/delays`: computed delay for specified trips/stops.
  - `/stops`, `/routes`, `/trips`: static transit data.
- Responsible for:
  - Binding static and realtime data.
  - Serving data to frontend or 3rd-party clients.
  - Maintaining database connections and service logic.

#### 4. `database/` (TimescaleDB)
- Houses:
  - **Static tables**:
    - `routes(route_id, name, color)`
    - `stops(stop_id, name, lat, lon)`
    - `trips(trip_id, route_id, service_id)`
    - `stop_times(trip_id, stop_sequence, arrival_time, departure_time)`
  - **Realtime tables**:
    - `vehicle_positions(timestamp, vehicle_id, lat, lon, trip_id)`
    - (potentially) `delay_events` or `stop_update` tables.
- Uses TimescaleDB extension to optimize time-series queries.

#### 5. `frontend/` (React + MapLibre)
- Displays:
  - Map with bus icons updated in near real-time.
  - Color/label indicating delay per vehicle.
- Architecture:
  - `src/components/MapView.js` – renders MapLibre map & vehicle markers.
  - `src/api.js` – client-side fetch calls to backend API.
- Development:
  - Install via `npm install`.
  - Start with `npm start` (default: `localhost:3000`).
  - Configured to query backend at `http://localhost:8000` (or via env var).

#### 6. `docker-compose.yml`
- **Services**:
  - `db`: TimescaleDB.
  - `backend`: FastAPI + subscriber + import script.
  - `frontend`: (optional, if containerized) React app.
- **Volumes**:
  - Database storage mounted to persist data.
- **Image build**:
  - Backend built via its Dockerfile.
  - Frontend may be served via static host or served separately.

---

### 💡 Developer Highlights

- **Module structure**:
  - `main.py`: application entrypoint.
  - `routers/`: FastAPI route definitions.
  - `models/` or `schemas/`: DB table and Pydantic schemas.
  - `services/`: Business logic – parsing, calculations, subscribers.
- **JSON Schemas**:
  - API responses follow Pydantic models (e.g. `Vehicle`, `StopTime`, `DelayReport`).
- **Polling vs. Streaming**:
  - Frontend polls REST endpoints at intervals.
  - Backend ingest is near-real-time via MQTT.
- **Schedules refresh**:
  Run `import_gtfs.py` when new GTFS schedules are published. Refreshes static tables.
- **Delay Calculation**:
  - Find scheduled arrival time for the `stop_id` matching `trip_id`.
  - Compute `delta = live_ts − scheduled_ts`.
  - Store or compute on-demand for API delivery.

---

### ✅ Summary for Developers

1. Familiarize with the code by starting with the REST API in FastAPI: routes, models, and logic.
2. Review GTFS import script to understand static data handling.
3. Explore MQTT subscriber for real-time data flow into DB.
4. Study DB schema via `init_timescale.sql` or inspect tables manually.
5. Run in development mode using Docker Compose, then test the system end-to-end:

```bash
docker-compose up -d
docker-compose exec backend python scripts/import_gtfs.py
```

6. Frontend inspection: see how visual mapping works via React/MapLibre.
7. To extend features (e.g. new endpoints, map layers, data analytics), update the appropriate component and add tests.

---

This `overview.md` provides both a bird’s-eye view and under-the-hood walkthrough of Bussikartta. Let me know if you’d like additional sections!
