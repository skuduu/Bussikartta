# 🚍 Bussikartta V3 - Project Architecture Document

_Last updated: 2025-06-17_

---

## 🧭 Project Vision

- Create a fully scalable, performant, and professional transit map and backend for Helsinki Region Transit (HSL).
- Realtime vehicle tracking, historical data storage, fast API access, and frontend map rendering.
- Entirely self-hosted on Synology NAS with zero external dependencies or recurring costs.
- Highly maintainable, documented, and easily extendable for future features.

---

## 🔧 Technology Stack

| Layer        | Technology            | Notes                        |
|--------------|------------------------|-------------------------------|
| Frontend     | React + MapLibre GL JS | Map rendering, UI/UX |
| Styling      | TailwindCSS            | Fully responsive |
| Backend API  | FastAPI (Python 3.12)  | REST & WebSocket |
| Database     | TimescaleDB (Postgres 15) | Historical & Realtime time-series |
| Caching      | Redis (optional future) | Small fast key-value cache |
| Message Broker | MQTT (HSL HFP)       | Realtime high-frequency vehicle positions |
| Deployment   | Docker Compose         | Fully containerized |
| Map Tiles    | TileServer GL          | Self-hosted MBTiles |
| Reverse Proxy | Synology NGINX (or Traefik) | TLS termination |
| Backups      | Docker automated volume backups | Full dbdata volume backup |

---

## 🔌 Data Sources

| Source       | Endpoint |
|--------------|----------|
| GTFS Static  | https://api.digitransit.fi/gtfs/hsl.zip |
| GTFS-RT Vehicles | https://realtime.hsl.fi/realtime/vehicle-positions/v2/hsl |
| GTFS-RT Trip Updates | https://realtime.hsl.fi/realtime/trip-updates/v2/hsl |
| GTFS-RT Alerts | https://realtime.hsl.fi/realtime/service-alerts/v2/hsl |
| MQTT HFP | mqtts://mqtt.hsl.fi:8883 (hfp/v2/journey/ongoing/#) |
| Digitransit GraphQL | https://api.digitransit.fi/routing/v2/hsl/gtfs/v1 |

---

## 🚀 API Design Principles

- Bounding-box filtering for stops & vehicles
- Parameterized endpoints:
  - `/vehicles?bbox=...`
  - `/stops?bbox=...`
  - `/timetable?stop_id=...&date=...`
  - `/alerts?route_id=...`
- Minimal JSON payloads
- Pagination for large queries
- Fully decoupled frontend & backend

---

## 📊 Database Schema Plan

**Static GTFS Tables:**

| Table         | Description |
|---------------|-------------|
| stops         | Stop locations |
| routes        | Route definitions |
| trips         | Trip patterns |
| stop_times    | Timetables |
| calendar      | Service dates |
| fare_rules    | Fare system |
| feed_info     | GTFS versioning |

**Realtime Tables (Timescale Hypertables):**

| Table           | Description |
|------------------|-------------|
| vehicle_positions_rt | GTFS-RT vehicle positions |
| trip_updates_rt  | GTFS-RT trip updates |
| service_alerts_rt | GTFS-RT alerts |
| hfp_positions    | MQTT HFP realtime updates |

---

## 🧮 Indexing Strategy

- Composite indexes on `stop_id`, `trip_id`, `timestamp`
- GIST spatial indexes for lat/lon bounding box queries
- TimescaleDB automatic chunking by time

---

## 🏗 Container Layout (Docker Compose)

| Service   | Purpose | Ports |
|-----------|---------|-------|
| api-server | FastAPI backend | 8007:5000 |
| db         | TimescaleDB      | 15432:5432 |
| backup     | Automated backup | N/A |
| frontend   | React app (future) | 8008:80 |
| proxy (optional) | NGINX or Traefik | 443:443 |

> Backup container uses bind mount of `dbdata` volume for full data durability.

---

## 🔐 Security Design

- API keys and credentials stored in `.env` files, never embedded in frontend
- Docker secrets (optionally for production)
- Frontend only communicates with API proxy
- MQTT credentials handled server-side
- Full backups stored outside containers

---

## 🛡 Disaster Recovery

- Full `dbdata` volume bind mounted to NAS storage:  
  `/volume1/docker/hslbussit/repo/dbdata`
- Automated backup runs daily via backup container
- GitHub repository contains:
  - Full source code
  - Docker Compose config
  - Project architecture documentation
- Entire project reproducible via single `git clone && docker-compose up -d --build`

---

## 🔑 Ports and Endpoints Summary

| Component   | URL | Port |
|-------------|-----|------|
| Backend API | http://localhost:8007 | 8007 |
| Frontend (future) | http://localhost:8008 | 8008 |
| DB Internal | localhost | 5432 |
| NAS Volume  | /volume1/docker/hslbussit/repo/dbdata | bind mount |
| MQTT Broker | mqtt.hsl.fi | 8883 |

---

## 🌐 Domain Mapping (Planned Future)

| DNS Name | Purpose |
|----------|---------|
| `bussikartalla.skuduu.com` | Frontend |
| `bussikartta-api.skuduu.com` | API Backend |
| (optional) `tiles.skuduu.com` | Map TileServer |

---

## 🔥 Performance Notes

- Instant load times even with large datasets
- No entire-dataset downloads; all queries filtered server-side
- Timescale hypertables optimized for high write volume and historical queries

---

## 🚩 Outstanding Phases

- ✅ Phase 1: Full backend bootstrapped (current state ✅)
- 🚀 Phase 2: Start application development (GTFS static loader, initial endpoints)
- 🚀 Phase 3: Realtime ingestion layer (GTFS-RT fetcher, MQTT listener)
- 🚀 Phase 4: Frontend UI development
- 🚀 Phase 5: Deployment polishing (domains, certs, reverse proxy)

---

# ✅ Status: Bussikartta v3 foundation fully locked
