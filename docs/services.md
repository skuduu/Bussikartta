# Bussikartta Service Matrix

This document outlines all services that make up the Bussikartta architecture, their purposes, interfaces, and interdependencies.

## 🚀 Runtime Services

### 1. mqtt-ingest

| Property       | Description                                                         |
| -------------- | ------------------------------------------------------------------- |
| **Role**       | Subscribes to HSL's MQTT broker and ingests live vehicle telemetry. |
| **Feeds**      | `mqtt.hsl.fi`, topic `/hfp/v2/journey/ongoing/vp/bus/#`             |
| **Writes to**  | `mqtt_hfp` table in TimescaleDB.                                    |
| **Tech**       | Python + Paho MQTT + psycopg2                                       |
| **Log Format** | JSON-structured console + `/var/log/mqtt_ingest.log`                |
| **Failsafe**   | Restarted by `mqtt_watchdog.sh` if insert lag exceeds threshold     |

---

### 2. vehicle-ingest

| Property       | Description                                                    |
| -------------- | -------------------------------------------------------------- |
| **Role**       | Fetches and stores GTFS-RT vehicle positions (protobuf)        |
| **Feeds**      | `https://api.digitransit.fi/realtime/vehicle-positions/v1/hsl` |
| **Writes to**  | `vehicle_positions` table in TimescaleDB                       |
| **Tech**       | Python + requests + gtfs-realtime-bindings                     |
| **Log Format** | stdout + optional `vehicle_watchdog.log`                       |
| **Failsafe**   | Periodic polling, restarted by watchdog if lagged              |

---

### 3. backend (FastAPI)

| Property       | Description                                                       |
| -------------- | ----------------------------------------------------------------- |
| **Role**       | REST API for clients, joins live and static data                  |
| **Endpoints**  | `/vehicles`, `/routes`, `/stops`, `/trips`, `/delays`, etc.       |
| **Reads from** | `mqtt_hfp`, `vehicle_positions`, `routes`, `stops`, `trips`, etc. |
| **Tech**       | FastAPI + Pydantic + SQL                                          |
| **Docs**       | Available at `/docs` (Swagger UI)                                 |

---

### 4. frontend

| Property        | Description                                        |
| --------------- | -------------------------------------------------- |
| **Role**        | React-based web app showing live vehicle positions |
| **Built With**  | React, Tailwind, MapLibre GL JS                    |
| **Data Source** | Polls `/vehicles` endpoint every 1s                |
| **Map**         | MapLibre + OpenStreetMap raster tiles              |
| **UI Features** | (in progress) delay coloring, route display        |

---

### 5. gtfs-static

| Property     | Description                                                      |
| ------------ | ---------------------------------------------------------------- |
| **Role**     | Fetches GTFS ZIP and imports static tables (routes, stops, etc.) |
| **Source**   | `https://infopalvelut.storage.hsldev.com/gtfs/hsl.zip`           |
| **Tables**   | `routes`, `trips`, `stops`, `stop_times`, etc.                   |
| **Run Mode** | Manual or scheduled script `import_gtfs.py`                      |
| **Triggers** | DB update, resets baseline for delay logic                       |

---

### 6. TimescaleDB

| Property        | Description                                                               |
| --------------- | ------------------------------------------------------------------------- |
| **Role**        | Core database with both static and time-series GTFS data                  |
| **Extensions**  | TimescaleDB, (optional) PostGIS                                           |
| **Tables**      | `mqtt_hfp`, `vehicle_positions`, `routes`, `trips`, `stops`, `stop_times` |
| **Access**      | via backend or ingestion processes                                        |
| **Persistence** | Volume-mounted for Docker, backed up by `backup.sh`                       |

---

### 7. backup.sh

| Property     | Description                                 |
| ------------ | ------------------------------------------- |
| **Role**     | Dump TimescaleDB to timestamped backup file |
| **Run Mode** | Manual or scheduled cronjob                 |
| **Target**   | `./backups/*.sql.gz`                        |
| **Restore**  | Standard `psql` restore flow                |

---

## 🌐 Observability & DevOps

* `mqtt_watchdog.sh`, `vehicle_watchdog.sh`: Monitor and auto-restart ingestion services.
* `/var/log/*_watchdog.log`, `/var/log/*_ingest.log`: Primary logs.
* `crontab`: Triggers watchdogs every 2 min.

---

> All services are dockerized via `docker-compose.yml`.

See also:

* [project\_architecture.md](./docs/project_architecture.md)
* [gtfs\_data\_handling.md](./docs/gtfs_data_handling.md)
* [frontend\_architecture.md](./docs/frontend_architecture.md)
* [overview.md](./docs/overview.md)
