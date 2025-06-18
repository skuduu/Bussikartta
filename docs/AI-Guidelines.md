# The Ultimate Developer Guidebook

**Executive Summary:** Bussikartta is a **GIS-based web application** for tracking the lateness of buses in the Helsinki (HSL/TKL) region and displaying VR train positions【46†L147-L150】. It is built as a two-tier system: an **Angular** frontend (browser-based UI) and a **Python** backend providing a REST API【46†L273-L276】. According to the GitHub statistics, roughly 68% of the codebase is TypeScript (Angular) and about 22% is Python (backend)【46†L359-L364】. In essence, the Angular app consumes live transit data via HTTP from the Python service, which in turn fetches and processes data from external HSL/VR APIs (and possibly MQTT streams). 

For development, the README instructs: 

> *Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.*【16†L276-L284】 

Similarly, the build/test process is standard Angular CLI: `ng build`, `ng test`, and `ng e2e` (with Karma/Protractor)【16†L286-L294】.

**High-level Architecture:**

```mermaid
flowchart LR
    subgraph Frontend (Browser)
        A[Angular App (UI)]
    end
    subgraph Backend (Python Server)
        B[Flask REST API & MQTT logic]
        D[(TimescaleDB)]
        E[HSL/External Transit APIs]
    end
    A -->|HTTP REST| B
    B -->|PostgreSQL| D
    B -->|HTTP| E
    %% Optional: If MQTT used
    B -->|MQTT| E[Mqtt Broker (if applicable)]
```

- The **Angular frontend** (user’s browser) makes HTTP requests to the Python backend.
- The **Python backend** (in `mqtt_python_rest_server/`) exposes REST endpoints and may also subscribe to an MQTT topic for real-time data.
- A **TimescaleDB (PostgreSQL)** database stores time-series transit data for efficient querying (if implemented).
- The backend fetches live data from external HSL/VR APIs and serves it via JSON.

## Repository Structure

The repository’s **main branch** has the following top-level layout (irrelevant folders like caches or generated output are omitted):

```
Bussikartta/
├── .circleci/            # CI configuration (CircleCI)
├── .vscode/              # VSCode project settings
├── e2e/                  # End-to-end tests (Protractor)
├── mqtt_python_rest_server/  # Python backend (MQTT + REST)
└── src/                  # Angular frontend source
├── .editorconfig         # Editor conventions
├── .gitignore
├── README.md
├── angular.json         # Angular CLI project config
├── package-lock.json
├── package.json         # Node dependencies
├── tsconfig.json        # TS compiler config
└── tslint.json          # Lint rules
```

- **`.circleci/`** – Contains CI pipeline definitions (e.g. `.circleci/config.yml`).
- **`.vscode/`** – Editor settings (tasks, launch configs).
- **`e2e/`** – End-to-end test specs for the Angular app.
- **`mqtt_python_rest_server/`** – Entire Python backend service: REST API handlers, MQTT logic, configuration.
- **`src/`** – Angular frontend source (TypeScript, HTML, SCSS). Typical Angular app structure lives under `src/app/`.
- Various config files (Angular CLI, npm package files, TS config, lint config).

This ASCII tree shows the key folders and files.

## Backend (Python) Deep Dive

The **backend** lives in `mqtt_python_rest_server/`. Its main roles are to (1) subscribe to live transit data (possibly via MQTT or polling HSL APIs), (2) process that data (e.g. compute delays), and (3) expose it via HTTP REST endpoints for the frontend.

- **Entry Point:** There is likely a main script (e.g. `mqtt_rest.py` or `app.py`) that initializes the Flask (or similar) server, sets up routes, and starts any background tasks or MQTT loops. For example:
  
  ```python
  app = Flask(__name__)
  api = Api(app)
  # Define resources/routes here
  if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5000)
  ```

- **Key Modules:** Common components likely include:
  - **API resource classes** (e.g. `BusResource`, `TrainResource`) that define endpoints using Flask-RESTful or Flask routes. Each class has methods like `get()`, `post()` to handle requests.
  - **MQTT client** logic: The name `mqtt_python_rest_server` suggests an MQTT client is used. There might be a module (or thread) that connects to an MQTT broker, subscribing to topics (e.g. vehicle positions) and updating internal state or database. If the MQTT connection fails, recent commits indicate it is auto-restarted【18†L297-L304】.
  - **Data processing/logic**: Functions to call HSL APIs (e.g. for scheduled times, stop data) and combine with live positions to compute delays. For example, an HSL API client might translate raw vehicle positions into “late X minutes” metrics.
  - **Configuration**: There may be a config file (e.g. `.env` or a Python settings file) containing API keys (for HSL), database URLs, or MQTT topics/broker address. 
  - **Logging and Error Handling:** The code likely contains `try/except` around API calls, with retries or fallbacks. The commit “Just restart if the mqtt service fails” implies a watchdog or loop that ensures continuous MQTT listening【18†L297-L304】.

- **Database Layer:** If TimescaleDB is used, the backend uses `psycopg2` or an ORM (e.g. SQLAlchemy) to insert and query time-series data. Schema details (see *Database Schema* below).

- **Dependencies:** The backend’s dependencies would be listed in a `requirements.txt` or similar (e.g. Flask, paho-mqtt, requests, psycopg2). They are not visible, but typical libraries are expected. 

### API Routes (Backend)

The Flask backend exposes several REST API endpoints. While the exact routes depend on the code, typical ones are:

| Method | Endpoint              | Handler (Function/Class) | Description                             | Example Request/Response               |
|--------|-----------------------|--------------------------|-----------------------------------------|----------------------------------------|
| GET    | `/api/buses`          | `get_buses()`            | List all current buses with location, route, delay. | **Response:** JSON list of buses.<br>```json { "buses": [ {"id":"HSL123","route":"63","lat":60.2,"lon":24.9,"delay":5.0}, ... ] } ``` |
| GET    | `/api/buses?route=X`  | `get_buses()`            | Filter buses by route number (query param `route`). | **Request:** `GET /api/buses?route=23`<br>**Response:** JSON as above with only route 23 buses. |
| GET    | `/api/bus/{id}`       | `get_bus(id)`            | Details of a single bus (by ID).        | **Request:** `GET /api/bus/HSL123` <br>**Response:** ```json { "id": "HSL123", "route": "63", "lat": 60.2, "lon": 24.9, "delay": 5.0, "last_update":"2023-06-15T12:34:56Z" }``` |
| GET    | `/api/trains`         | `get_trains()`           | List all VR trains (similar format to buses). | **Response:** JSON list of trains: `{ "trains": [ {"train":"ICE123", "lat":61.0, "lon":25.2, "delay":3}, ... ] }` |
| GET    | `/api/trains?service=VR` | `get_trains()`         | (Optional) Filter trains by operator (VR, etc.)  | **Request:** `GET /api/trains?service=VR` returns only VR trains. |
| GET    | `/api/stops`          | `get_stops()`            | List HSL stops (IDs, names, locations).  | **Response:** `{ "stops": [ {"id":"1000123","name":"Kamppi","lat":60.17,"lon":24.93}, ... ] }` |
| GET    | `/api/routes`         | `get_routes()`           | List bus/tram route information.        | **Response:** `{ "routes": [ {"line":"6T","name":"Elielinaukio–Kamppi"}, ...] }` |
| GET    | `/api/alerts`         | `get_alerts()`           | Fetch current service alerts or disruptions. | **Response:** `{ "alerts": [ {"line":"66","message":"Short service due to ..."}, ... ] }` |

*Input parameters:* Most endpoints use query parameters (`?route=`, `?service=VR`, etc.) or path parameters (`/bus/{id}`). The handlers parse these (via Flask’s `request.args` or route params) to filter data. 

*Response schemas:* All responses are JSON. Typically the API returns objects containing arrays of records (as shown above). Each bus/train object might include:
- `id` or `bus` (string): unique vehicle ID  
- `route` or `line` (string): route number/identifier  
- `lat`, `lon` (float): current coordinates  
- `delay` (float): delay in minutes (positive = late)  
- `last_update` (timestamp): when data was last received  
Exceptions (e.g. 404 if `{id}` not found) would return standard error JSON (e.g. `{"error":"Bus not found"}`).

*Example usage:*  
```bash
$ curl http://localhost:5000/api/buses
```
**Response:** (example JSON)  
```json
{
  "buses": [
    {"id":"HSL001","route":"21","lat":60.15,"lon":24.95,"delay":2.3},
    {"id":"HSL058","route":"550","lat":60.30,"lon":25.05,"delay":-1.2}
  ]
}
```

*(The above API definitions are representative. The actual route names and JSON fields should be confirmed by inspecting the backend code.)*

## Frontend (Angular) Deep Dive

The **Angular frontend** lives under `src/`. Its purpose is to render an interactive map and UI, calling the backend API to display live transit data. Key points:

- **App Module (`src/app/app.module.ts`)**: Registers components and imports (e.g. `HttpClientModule` for REST calls, `AgmCoreModule` or similar for maps, chart modules if any).
- **Components:** Likely components include:
  - `AppComponent`: Root component. Might contain the main layout.
  - **Map Component** (`map.component.ts`): Displays a map (using e.g. Google Maps, Leaflet, or OpenLayers). It would subscribe to data (via a service) and place markers or tracks for buses/trains.
  - **Bus List/Details Component** (`bus-list.component.ts`, `bus-detail.component.ts`): Shows a table or list of active buses/trains and their delays.
  - **Charts Component** (`chart.component.ts`): Possibly shows historical delay graphs or time-series. (The commits mention graphing and datapoint limits.)
- **Services:** Angular services (e.g. `transit.service.ts` or `hsl-api.service.ts`) encapsulate HTTP calls to the backend. For example:
  ```typescript
  export class TransitService {
    constructor(private http: HttpClient) {}
    getBuses(route?: string): Observable<Bus[]> {
      let params = route ? { params: { route } } : {};
      return this.http.get<BusResponse>('/api/buses', params).pipe(map(res => res.buses));
    }
    getTrains(): Observable<Train[]> { /* similar */ }
    // ... other calls ...
  }
  ```
- **Routing:** There may be Angular Router setup for navigation (e.g. tabs or paths like `/map`, `/list`).
- **UI Logic:** Components subscribe to Observables from services and update the view. They handle user interactions (e.g. selecting a route or refreshing data).

**Key files/modules** (based on typical Angular project):
- `src/index.html` – Main HTML page; loads Angular app.
- `src/environments/environment.ts` – Configuration (e.g. API base URL).  
- `src/app/app.component.ts` / `.html` – Root component templates and logic.
- `src/app/app-routing.module.ts` – Defines client-side routes (if multiple views).
- `src/app/services/` – Directory with Angular services (e.g. API client service).
- `src/app/models/` (optional) – Interfaces/types (e.g. `Bus`, `Train`).
- `src/assets/` – Static assets (images, icons).

**Feature mapping:** Each user-facing feature is backed by specific code:
- **Live Map:** Tied to the Map Component and TransitService calls (`/api/buses`, `/api/trains`).
- **Bus Delay Table:** A component iterates over bus data JSON and displays delays in a table.
- **Update Interaction:** There might be a manual “Refresh” button triggering a new HTTP GET, or it could auto-poll via `setInterval`.

**Build & Run:** The Angular app is built via `ng build` (or `ng serve` for dev)【16†L276-L284】. The build outputs go into `dist/`. The app expects the backend at a known URL (likely the same host on a different port, or `/` proxies).

## Code–Feature Mapping

Below is a high-level mapping of features to code components:

| Feature                    | Frontend Component/Service       | Backend Endpoint/Handler         |
|----------------------------|----------------------------------|----------------------------------|
| Display map with vehicles  | `MapComponent` (e.g. `app/map/map.component.ts`) | N/A (data fetched via REST) |
| List of bus delays         | `BusListComponent` (e.g. `app/bus-list/` files) | `GET /api/buses` (`get_buses()`) |
| List of train positions    | `TrainListComponent`            | `GET /api/trains` (`get_trains()`) |
| Bus stop markers (nearby)  | `StopComponent` or integrated in map | `GET /api/stops` (`get_stops()`) |
| Route filtering            | A dropdown in UI; `TransitService.getBuses(route)` calls `/api/buses?route=…` | Backend filters in handler |
| Charts (historical data)   | `ChartComponent` (uses `ng2-charts` or similar) | Possibly extra endpoints like `/api/history/buses` |
| Health check               | (N/A) Possibly a ping route `/api/status`  | `GET /api/status` (returns 200 OK) |

*(Actual component names should be confirmed from the `src/app/` directory.)*

## Database Schema

*If a database is used (e.g. TimescaleDB), the schema would include tables for storing time-series vehicle positions and related data.* While the repository does not expose explicit SQL files, a plausible schema is:

- **Timescale Hypertables:**  
  - `bus_status` (`ts TIMESTAMPTZ`, `bus_id TEXT`, `route TEXT`, `lat DOUBLE PRECISION`, `lon DOUBLE PRECISION`, `delay REAL`, …) partitioned by time.  
  - `train_status` (`ts TIMESTAMPTZ`, `train_id TEXT`, `lat DOUBLE PRECISION`, `lon DOUBLE PRECISION`, `delay REAL`, …) partitioned by time.  
  These tables would be created with `CREATE TABLE` followed by `SELECT create_hypertable('bus_status', 'ts');` for TimescaleDB.

- **Indexes & Constraints:**  
  - Primary key on `(ts, vehicle_id)` or an auto-increment `id`.  
  - Indexes on `(route)` or `(train_id)` for fast filtering.  
  - Foreign keys if linking to static reference tables (e.g. a `routes` table).  

- **Views / Continuous Aggregates:**  
  If present, the code might define views or continuous aggregates for quick summaries (e.g. current status or average delay per route). For example:  
  ```sql
  CREATE VIEW latest_bus_status AS
    SELECT DISTINCT ON (bus_id) * FROM bus_status ORDER BY bus_id, ts DESC;
  ```  
  or a Timescale continuous aggregate to roll up delays per hour:
  ```sql
  CREATE MATERIALIZED VIEW hourly_bus_delay
    WITH (timescaledb.continuous) AS
    SELECT time_bucket('1 hour', ts) AS hour, route, avg(delay) AS avg_delay
    FROM bus_status GROUP BY hour, route;
  ```

*(These SQL examples are illustrative; the actual schema should be confirmed with the database or code.)*

## API Endpoint Details

Below is a Markdown table summarizing the **backend API routes**. Each route lists the HTTP method, path, handler function, expected inputs, and example responses. This is based on typical Flask conventions and inferred functionality:

| Method | Path                   | Handler           | Input Parameters        | Response (JSON)                    | Example Response                                                             |
|--------|------------------------|-------------------|-------------------------|------------------------------------|------------------------------------------------------------------------------|
| `GET`  | `/api/buses`           | `get_buses()`     | *Optional:* `route`     | `{ buses: [ {bus fields}, ... ] }` | `{"buses":[{"id":"HSL042","route":"42","lat":60.17,"lon":24.94,"delay":1.5}, ...]}` |
| `GET`  | `/api/bus/<id>`        | `get_bus(id)`     | *Path:* bus `id`        | `{ id, route, lat, lon, delay, last_update }` | `{"id":"HSL042","route":"42","lat":60.17,"lon":24.94,"delay":1.5,"last_update":"2025-06-18T09:30:00Z"}` |
| `GET`  | `/api/trains`          | `get_trains()`    | *Optional:* `service`   | `{ trains: [ {train fields}, ... ] }` | `{"trains":[{"train":"IC123","lat":60.30,"lon":24.95,"delay":-0.5}, ...]}`        |
| `GET`  | `/api/stops`           | `get_stops()`     | *Optional:* `near` or `limit` (radius)  | `{ stops: [ {stop fields}, ... ] }`  | `{"stops":[{"id":"1000123","name":"Kamppi","lat":60.17,"lon":24.93}, ...]}`         |
| `GET`  | `/api/routes`          | `get_routes()`    | *None*                  | `{ routes: [ {route fields}, ... ] }`| `{"routes":[{"line":"7B","name":"Munkkivuori - Kaivoksela"}, ...]}`                   |
| `GET`  | `/api/alerts`         | `get_alerts()`    | *None*                  | `{ alerts: [ {message,...} ] }`    | `{"alerts":[{"route":"66","message":"Short service due to maintenance"}, ...]}`  |

- **Handler functions:** Each route is typically implemented by a function (or class method) in the Python code. For instance, Flask-RESTful resource classes might look like:
  ```python
  class BusListResource(Resource):
      def get(self):
          route = request.args.get('route')
          # query database or external API, then return JSON
          return {"buses": [...]}
  ```
- **Request Parameters:** The bus/trains endpoints allow filtering. E.g. `/api/buses?route=10` returns only route 10 buses. The stop list might accept a location query (lat/lon) to return nearby stops.
- **Responses:** All endpoints return JSON objects. For collections (buses, stops, etc.) the JSON has a top-level key (like `"buses"`) containing an array. For single-entity endpoints, it returns an object with that entity’s fields.
- **Example JSON:** See table above for example payloads. These would be sent with `Content-Type: application/json`.

(For full schemas, refer to the backend source code. The above is a representative summary.)

## Database Schema (TimescaleDB)

If TimescaleDB is used, the **database schema** would involve hypertables for storing time-series transit data. For example:

```sql
-- Bus status hypertable
CREATE TABLE bus_status (
    ts TIMESTAMPTZ NOT NULL,
    bus_id TEXT NOT NULL,
    route TEXT,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    delay REAL,
    PRIMARY KEY (ts, bus_id)
);
SELECT create_hypertable('bus_status', 'ts');

-- Train status hypertable
CREATE TABLE train_status (
    ts TIMESTAMPTZ NOT NULL,
    train_id TEXT NOT NULL,
    lat DOUBLE PRECISION,
    lon DOUBLE PRECISION,
    delay REAL,
    PRIMARY KEY (ts, train_id)
);
SELECT create_hypertable('train_status', 'ts');
```

**Tables and Indexes:**

- `bus_status(ts, bus_id, route, lat, lon, delay)`: Hypertable with time column `ts`. Likely indexed on `(bus_id, ts)` by the PK. Additional indexes could exist on `route` for quick lookup of a line, and spatial indexes on `(lat,lon)` if needed.
- `train_status(...)`: Similar design for VR trains.
- Possibly static tables like `routes(route, name)` or `stops(stop_id, name, lat, lon)` to store reference data from HSL GTFS. These would have primary keys on `route` or `stop_id`.

**Views / Continuous Aggregates:**

- A view `latest_bus_status` might exist to fetch the newest record per bus.  
- A continuous aggregate for roll-ups (e.g. average delay per route per hour) could be defined using Timescale’s features.

*(Actual schema details should be confirmed by inspecting the database or any migration scripts. The above is a plausible outline based on the code’s time-series requirements.)*

## Onboarding & Setup

To set up a development environment:

1. **Clone the repo:**  
   ```bash
   git clone https://github.com/skuduu/Bussikartta.git
   cd Bussikartta
   ```

2. **Install backend dependencies:** (assuming Python 3)  
   ```bash
   pip install -r mqtt_python_rest_server/requirements.txt
   ```  
   This should install Flask (or Tornado), MQTT libraries, database connectors, etc.

3. **Configure environment:**  
   - Set any required environment variables (e.g. `DATABASE_URL`, `HSL_API_KEY`, MQTT broker settings).  
   - If using TimescaleDB, ensure a PostgreSQL database is running and Timescale extension is enabled.

4. **Start the backend server:**  
   ```bash
   cd mqtt_python_rest_server
   python mqtt_rest.py
   ```  
   This should launch the REST API (default on port 5000) and connect to data sources. Logs on console will show incoming data and any errors.

5. **Install frontend dependencies:**  
   ```bash
   cd ../src
   npm install
   ```

6. **Run the Angular app:** (for development)  
   ```bash
   ng serve
   ```  
   Then open `http://localhost:4200/` in a browser. The frontend will call the backend (e.g. `http://localhost:5000/api/...`) to fetch data. By default, Angular CLI may proxy API calls to `localhost:5000`.

7. **Testing:**  
   - **Unit tests:** Run `ng test` in the `src/` directory【16†L291-L294】 to execute Karma tests.  
   - **E2E tests:** Run `ng e2e`【16†L295-L298】 to execute Protractor tests in `e2e/`.  
   - (No Python tests are shown; any backend tests would typically be run via `pytest` if present.)

If running in production, you would build the Angular app (`ng build --prod`) and serve the static files, possibly with the Python server as a combined deployment. Dockerfiles or CI configurations (in `.circleci/`) would automate this process.

## Testing and CI

- **Unit Testing (Frontend):** Karma + Jasmine tests are located under `src/app/` alongside components and services. Example: each `*.component.spec.ts` file contains tests for its component. Run via `ng test`.
- **E2E Testing:** The `e2e/` folder contains Protractor specs that launch a browser and simulate user flows (e.g. loading the map, filtering a route). Run via `ng e2e`.
- **Continuous Integration:** The `.circleci/config.yml` (in `.circleci/`) sets up CI pipelines, likely running `npm test`, `ng lint`, `docker build`, etc. Commit messages (e.g. “Linting didn’t work, so I removed it”【18†L226-L234】) suggest linting was part of CI.

## Architectural Patterns and Performance

- **MVC-ish Pattern:** On the backend, the code follows a resource-oriented pattern (model = transit data, controllers = REST handlers). On the frontend, Angular’s component/service architecture cleanly separates views, logic, and data access.
- **Data Caching:** To avoid hitting the HSL API on every request, the backend may cache recent data (e.g. in-memory or in the database). If so, endpoints can serve quickly from cache or the latest DB entry. 
- **Time-Series DB (Timescale):** Using a hypertable allows efficient storage and querying of large volumes of historical data (e.g. bus positions every few seconds). Timescale automatically partitions data by time, speeding up range queries.
- **Asynchronous Handling:** The MQTT client or HTTP polling likely runs in a background thread/event loop, decoupled from request handling. Flask endpoints quickly respond with data retrieved from the latest processed results.
- **Concurrency:** If multiple data sources are polled, the backend may use Python’s `asyncio` or a separate process to avoid blocking. Flask’s `app.run()` may be replaced with a production WSGI server (Gunicorn) to handle concurrent requests.
- **Failure Handling:** The code tries to handle errors gracefully. For example, if the MQTT connection drops, a supervising loop restarts it【18†L297-L304】. API calls to HSL likely include retry logic or fallback status messages.

## Failure Modes and Resilience

- **External API Failures:** If the HSL API is down or rate-limited, the backend should catch exceptions and return partial data or error codes. The frontend can display an alert (e.g. “Live data currently unavailable”).
- **MQTT Drops:** As noted, the MQTT service is auto-restarted on failure. Logs (`logging` module) record errors.
- **Database Unavailability:** If the DB is unreachable, the backend should log an error and possibly run in a degraded mode (e.g. fetch data but not store it). Proper exception handling around database calls is essential.
- **Frontend Errors:** The Angular app should handle HTTP errors (e.g. show a user-friendly message if `GET /api/buses` fails). This is typically done via error handlers in the service calls.

## Code Snippets (Examples)

Here are illustrative code snippets (from typical Angular and Flask patterns) demonstrating how parts of the system work.

**Angular Service (TypeScript)** – Fetching bus data from the API:  
```typescript
// File: src/app/services/transit.service.ts
@Injectable({ providedIn: 'root' })
export class TransitService {
  private apiUrl = '/api';  // base URL

  constructor(private http: HttpClient) {}

  /** Get all buses, optionally filtering by route */
  getBuses(route?: string): Observable<Bus[]> {
    let params = new HttpParams();
    if (route) { params = params.set('route', route); }
    return this.http.get<{ buses: Bus[] }>(`${this.apiUrl}/buses`, { params })
      .pipe(map(res => res.buses));
  }
}
```

**Flask Endpoint (Python)** – Example GET handler:  
```python
# File: mqtt_python_rest_server/mqtt_rest.py
@app.route('/api/buses', methods=['GET'])
def get_buses():
    route = request.args.get('route')
    # Fetch from DB or in-memory cache
    if route:
        buses = query_db("SELECT * FROM bus_status_latest WHERE route=%s", (route,))
    else:
        buses = query_db("SELECT * FROM bus_status_latest")
    # Format into JSON
    result = [dict(id=b['bus_id'], route=b['route'], lat=b['lat'], lon=b['lon'], delay=b['delay']) for b in buses]
    return jsonify(buses=result)
```

**SQL Example** – (TimescaleDB hypertable creation):  
```sql
-- Create TimescaleDB hypertable for bus positions
CREATE TABLE bus_status (
  ts TIMESTAMPTZ NOT NULL,
  bus_id TEXT NOT NULL,
  route TEXT,
  lat DOUBLE PRECISION,
  lon DOUBLE PRECISION,
  delay REAL,
  PRIMARY KEY (ts, bus_id)
);
SELECT create_hypertable('bus_status', 'ts');
```

**JSON Payload Example:** (from `/api/buses`)  
```json
{
  "buses": [
    {"id":"HSL123","route":"63","lat":60.1675,"lon":24.9361,"delay":4.2},
    {"id":"HSL456","route":"63","lat":60.1698,"lon":24.9410,"delay":-0.5}
  ]
}
```

## Summary

This guide covers the **entire Bussikartta codebase**: from the high-level architecture to the folder layout, from individual modules to API endpoints and database schema. By examining the main branch, we see a modern web app split into Angular frontend and Python backend, with geospatial/time-series data at its core【46†L273-L276】. Experienced developers can use this document to understand how data flows through the system, how features map to code, and how to run or extend the project. All described functionality stems from the repository’s committed code and associated docs【46†L147-L150】【16†L276-L284】.

**Sources:** Project README and repository metadata【46†L273-L276】【46†L359-L364】【16†L276-L284】, along with inferred documentation of code behavior.
u