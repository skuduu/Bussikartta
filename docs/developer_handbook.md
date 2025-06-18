# Developer Handbook

## 📦 System Overview

This project is a **real-time bus tracking system** for Helsinki Region Transport (HSL), capable of rendering thousands of live vehicle positions on a blazing fast vector tile map.

---

## 🧭 Architecture Summary

- **Backend**: FastAPI-based Python service exposing REST & WebSocket
- **Frontend**: SolidJS + Vite with MapLibre GL JS
- **Map Tiles**: HSL vector tiles (online) or Tileserver-GL (offline)
- **Database**: TimescaleDB (PostgreSQL)
- **Deployment**: Full Docker setup
- **Data**: Static GTFS + MQTT-based real-time vehicle feeds

---

## 🚀 Getting Started

### ✅ 1. Clone the repository

```bash
git clone https://github.com/YOUR_ORG/bussikartta.git
cd bussikartta
```

### ✅ 2. Launch the stack

```bash
docker compose up -d
```

Then access:
- Backend REST: http://localhost:8007/vehicles
- WebSocket: ws://localhost:8007/ws
- (If configured) Tile Server: http://localhost:8080
- Frontend Dev Server: http://localhost:5173

---

## 🧱 Folder Structure (Key)

```
repo/
├── api/                  # FastAPI backend
├── ingestion/            # MQTT + GTFS-RT ingestors
├── gtfs_static/          # Static GTFS importer
├── docs/                 # Architecture and dev docs
├── tools/                # Watchdog scripts
├── Dockerfile            # Backend container
├── docker-compose.yaml   # Services & ports
└── init_timescale.sql    # DB schema
```

---

## 🧩 Frontend Overview (SolidJS)

| Element       | Stack/Choice           |
| ------------- | ---------------------- |
| Framework     | SolidJS                |
| Dev Server    | Vite (`npm run dev`)   |
| Map Engine    | MapLibre GL JS         |
| Updates       | WebSocket              |
| Volume        | Supports 5,000+ markers|

Frontend connects to backend via:
- `fetch` (initial load)
- `WebSocket` (live updates, every 1s)
- Offline tiles supported via `.mbtiles` if Tileserver-GL is running.

---

## 🛰 Backend API

| Method | Path         | Description                        |
|--------|--------------|------------------------------------|
| GET    | `/vehicles`  | Current live vehicle positions     |
| WS     | `/ws`        | Streams 1s real-time JSON objects  |

### JSON Format:

```json
{
  "vehicle_id": "1234",
  "label": "600N",
  "lat": 60.17,
  "lon": 24.94,
  "speed": 33.0,
  "timestamp": "2025-06-19T00:00:00Z"
}
```

---

## 🛠 Watchdog & Cron Tools

Located in `tools/`:

- `mqtt_watchdog.sh`: Verifies live MQTT ingestion is active
- `vehicle_watchdog.sh`: Checks if recent vehicles exist in DB

Example usage via crontab or log-based monitoring.

---

## 📄 Reference Documents

| File                                | Purpose                                |
|-------------------------------------|----------------------------------------|
| `docs/project_architecture_plan.md` | Locked architectural decisions         |
| `docs/frontend_architecture.md`     | Map and component logic                |
| `docs/services.md`                  | Ports and service overview             |
| `docs/gtfs_data_handling.md`        | Static transit schedule import process |

---

## 📚 GTFS Data

### Static Feed
- URL: https://infopalvelut.storage.hsldev.com/gtfs/hsl.zip
- Parser: `gtfs_static/main.py`
- Imports `stops`, `routes`, `trips`, `calendar`, etc.

### Realtime
- MQTT Broker: `mqtt.hsl.fi` (port 1883 or 8883)
- Topic: `/hfp/v2/journey/#`
- Listener: `ingestion/mqtt_hfp_ingest/main.py`
- Output Table: `mqtt_hfp`

---

## 🗺 Map Tiles

| Mode    | Details                                  |
|---------|------------------------------------------|
| Online  | `cdn.digitransit.fi/hsl-vector-map`      |
| Offline | Tilemaker (`.mbtiles`) + Tileserver-GL   |

To use offline mode, generate `.mbtiles` from `hsl.osm.pbf`, mount it in the container, and run a vector tile server.

---

## 🧼 Final Notes

- Backend written in idiomatic FastAPI, one route file per GTFS domain
- System built for high-concurrency WebSocket performance
- Fully portable and containerized for deployment

_Last updated: 2025-06-18T23:44:39.748611Z_
