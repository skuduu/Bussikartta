# Bussikartta Services (v1.1)

## 🧭 Core Services

| Service      | Type     | Port | Description                             |
| ------------ | -------- | ---- | --------------------------------------- |
| Frontend     | Vite Dev | 5173 | Development server                      |
| Frontend     | NGINX    | 80   | Static production deployment            |
| Backend      | Python   | 8007 | REST `/vehicles`, WebSocket `/ws`       |
| Map Tile API | HTTP     | 8080 | (Optional) Tileserver GL for `.mbtiles` |

---

## 🔌 External Dependencies

| Source         | Use                         |
| -------------- | --------------------------- |
| HSL Vector Map | `cdn.digitransit.fi`        |
| GTFS Static    | Manual `.zip`               |
| GTFS-RT        | Streamed by backend         |
| OSM PBF        | `hsl.osm.pbf` for Tilemaker |

---

## 🗺 Map Tile Service (Offline)

| Component     | Technology    | Details                             |
| ------------- | ------------- | ----------------------------------- |
| Generator     | Tilemaker     | Converts `.osm.pbf` to `.mbtiles`   |
| Tile Server   | Tileserver GL | Serves vector tiles from `.mbtiles` |
| Containerized | Docker        | Mounted local tile volume           |

---

## 🧱 WebSocket Details

| Endpoint  | `/ws`              |
| --------- | ------------------ |
| Format    | JSON per vehicle   |
| Frequency | Every second       |

```json
{
  "vehicle_id": "1234",
  "label": "600N",
  "lat": 60.17,
  "lon": 24.94,
  "speed": 33.0,
  "timestamp": "2025-06-19T00:00:00Z"
}
🐳 Container Names (Example)
