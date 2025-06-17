# Bussikartta

**Bussikartta** is a real-time public transport tracking system designed to visualize live vehicle locations on a map and measure their performance against scheduled transit data. It is built for the Helsinki region (HSL) and supports modular extension to other regions or data sources.

---

## 🚀 Overview

Bussikartta ingests live vehicle data from MQTT feeds and compares it against GTFS-based schedule data to compute real-time delays. It features:

- Real-time tracking of buses and other transit using MQTT.
- Delay calculation based on GTFS schedule data.
- Interactive map frontend (React + MapLibre).
- Backend REST API (FastAPI).
- Historical data storage with TimescaleDB.

---

## 🏗️ Architecture Summary

### Backend
- **FastAPI** for API routing and logic.
- **TimescaleDB** for storing static and dynamic transit data.
- **MQTT Subscriber** that ingests real-time HFP feed from HSL.
- **GTFS Ingestor** that parses and imports static schedules.
- Modular services managed via Docker Compose.

### Frontend
- Built with **React**, **Tailwind CSS**, and **MapLibre GL JS**.
- Displays live vehicle locations, delay status, and route info.
- Polling-based updates with optional WebSocket/MQTT expansion.
- Clean and responsive UI, optimized for performance and mobile use.

---

## 🧭 GTFS Data Handling

- Ingests static GTFS data (routes, stops, trips, timetables).
- Maintains database schema for cross-referencing real-time info.
- Enables delay computation and trip association via trip_id.
- Supports daily updates and verification of GTFS feed versions.
- Cross-references static and live data to enrich API responses.

---

## 🧱 AI-Led Development Workflow

- AI is the **only developer**; the user executes instructions.
- AI outputs full, production-ready files—never code snippets.
- Terminal commands must include folder context and be one-liners.
- Persistent shell aliases allowed for repetitive tasks.
- Logging must be built-in across all layers (backend, frontend, Docker, browser console).
- Active tasks are tracked and resumed after detours (debugging, inspections).
- Commands use Synology DSM 7.2.2 environment (vi, BBEdit).

See [docs/AI-Guidelines.md](docs/AI-Guidelines.md) for full development protocol.

---

## 📂 Repository Structure

- `backend/` — FastAPI application and MQTT/GTFS ingestors
- `frontend/` — React + Tailwind + MapLibre frontend (planned/active)
- `docs/` — Architecture, GTFS, frontend, AI guidelines
- `gtfs_static/`, `ingestion/` — Data ingestion services
- `docker-compose.yml` — Orchestration of services
- `backup.sh` — TimescaleDB backup utility

---

## 🧪 Quickstart

```bash
git clone https://github.com/skuduu/Bussikartta.git
cd Bussikartta
cp .env.example .env  # edit as needed
docker-compose up -d
docker-compose exec backend python scripts/import_gtfs.py
```

Access:
- API: [http://localhost:8000/docs](http://localhost:8000/docs)
- Frontend: [http://localhost:3000](http://localhost:3000) (if implemented)

---

## 📄 Documentation

- [Overview](docs/overview.md)
- [Project Architecture](docs/project_architecture.md)
- [GTFS Data Handling](docs/gtfs_data_handling.md)
- [Frontend Architecture](docs/frontend_architecture.md)
- [AI Development Rules](docs/AI-Guidelines.md)

---

*Bussikartta transforms open transit data into real-time, actionable insights for developers and commuters.*  
