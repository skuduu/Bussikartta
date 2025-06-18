# Bussikartta

Real-time public transport map for the HSL region. This project shows live bus locations on a blazing fast vector tile map and uses WebSocket for high-frequency updates.

---

## ✨ Features

- SolidJS + Vite frontend (ultra fast, minimal re-renders)
- MapLibre GL JS map engine
- Supports 5000+ vehicle markers updated via WebSocket
- HSL vector tile support (online) or local `.mbtiles` via Tileserver-GL
- Fully containerized (Docker) backend and infrastructure

---

## 🧱 Repository Structure

```
repo/
├── api/                  # Python backend (FastAPI-ready)
├── gtfs/                 # GTFS static + realtime tools
├── scripts/              # CLI utilities
├── tileserver/           # Optional offline tile server (vector)
├── docker-compose.yml    # Service orchestration
├── README.md             # This file
└── docs/                 # Architecture, development and data notes
```

---

## 🚀 Quickstart (Dev Mode)

```bash
git clone https://github.com/YOUR_ORG/bussikartta.git
cd bussikartta
docker compose up -d
```

Then visit:

- Frontend (dev): http://localhost:5173
- Backend REST: http://localhost:8007/vehicles
- Backend WebSocket: ws://localhost:8007/ws
- (Optional) Offline tiles: http://localhost:8080

---

## 📡 Backend API

### `/vehicles` (GET)

Returns array of vehicle objects:

```json
[
  {
    "vehicle_id": "1234",
    "label": "600N",
    "lat": 60.17,
    "lon": 24.94,
    "speed": 33.0,
    "timestamp": "2025-06-19T00:00:00Z"
  }
]
```

### `/ws` (WebSocket)

Streams JSON payloads every second with updated vehicle positions.

---

## 🔌 Map Tiles

- **Online**: HSL Vector Tiles from `cdn.digitransit.fi`
- **Offline**: Generated via Tilemaker → served via Tileserver-GL
- Compatible with OpenMapTiles & MapLibre GL JS

---

## 📄 Documentation

- `docs/project_architecture_plan.md` — Locked architecture plan
- `docs/frontend_architecture.md` — Frontend layout + rendering logic
- `docs/services.md` — Service & port overview
- `docs/gtfs_data_handling.md` — Vehicle data formats

---

## 🐳 Docker Containers

| Name               | Role                    |
| ------------------|-------------------------|
| `repo-api-server` | Backend (`/vehicles`, `/ws`) |
| `bussikartta-ui`  | Frontend (static build) |
| `bussikartta-map` | Optional tile server    |

---

## 👨‍💻 Dev Scripts

```bash
docker compose logs -f
docker compose exec api bash
npm run dev        # inside frontend if dev server is needed
```

---

© HSL Bussikartta 2025
