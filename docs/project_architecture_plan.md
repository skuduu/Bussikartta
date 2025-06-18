# Bussikartta Architecture Plan v1.0

## 1. 🛍 Frontend

| Element         | Choice                                                |
| --------------- | ----------------------------------------------------- |
| Framework       | SolidJS + Vite                                        |
| Map engine      | MapLibre GL JS                                        |
| Live updates    | WebSocket (1-second interval)                         |
| Marker volume   | Supports 5,000+ real-time vehicle markers             |
| Labels          | Vehicle label + speed overlay (e.g. "600N @ 34 km/h") |
| UI Enhancements | Optional: timestamp, clustering, trails               |
| Dev mode        | `npm run dev` via Vite                                |
| Deployment      | Docker or static build via NGINX                      |

## 2. 🚀 Backend

| Element            | Choice                                                  |
| ------------------ | ------------------------------------------------------- |
| Framework          | Python (current) with upgrade path to FastAPI           |
| Live transport     | WebSocket (primary), Polling (fallback)                 |
| Data format        | JSON: `{vehicle_id, label, lat, lon, speed, timestamp}` |
| WebSocket endpoint | `/ws` (planned)                                         |
| Containerization   | Yes (e.g. `repo-api-server-1` on port `8007`)           |

## 3. 🗌 Map Tiles

| Element             | Choice                                                         |
| ------------------- | -------------------------------------------------------------- |
| Online base map     | HSL Vector Tiles (`hsl-vector-map`)                            |
| Offline fallback    | Tilemaker for `.pbf` vector tiles                              |
| Offline tile server | Tileserver GL with local `.mbtiles`                            |
| Style compatibility | HSL / OpenMapTiles / MapLibre-ready                            |
| Deployment          | Docker container with mounted tile volume                      |
| OSM source          | `https://karttapalvelu.storage.hsldev.com/hsl.osm/hsl.osm.pbf` |

## 4. 🔌 Infrastructure

| Element              | Choice                                 |
| -------------------- | -------------------------------------- |
| Containerization     | Full Docker deployment                 |
| Reverse proxy        | Optional: NGINX / Traefik              |
| Data update interval | Offline tiles: manual, Vehicles: live  |
| Logging & Monitoring | Optional: container logs, dev overlays |

## 🔨 Locked Decisions

* SolidJS + Vite frontend
* MapLibre GL JS
* WebSocket for real-time transport
* Offline vector tiles via Tilemaker
* Vector tile hosting via Tileserver-GL
* Backend maintained and included in architecture
* Fully Dockerized infrastructure
