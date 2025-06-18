Bussikartta Developer Guidebook

Executive Summary & Onboarding Flow

Overview: Bussikartta is a GIS-based solution for tracking transit delays. It displays how late buses (HSL/TKL) are and shows vehicle positions (including VR trains) on an interactive map. The system has two parts: a Python/TimescaleDB backend and a modern web frontend (React+TypeScript). Real-time data comes from HSL’s MQTT High-Frequency Positioning (HFP) API (mqtt.hsl.fi, port 1883/8883), and static schedule data comes from GTFS feeds. The backend (FastAPI) ingests data into TimescaleDB, and the frontend (React + Tailwind + MapLibre GL) fetches it via REST APIs. Containerization (Docker Compose) is used for TimescaleDB, backend and possibly frontend.

Deploy topology:

graph LR
  HFP[HSL MQTT Broker (/hfp/v2/journey)] -->|stream| MQTTClient[Backend MQTT Ingest]
  GTFS[Static GTFS Feed] -->|import| GTFSImporter[Backend GTFS Import]
  MQTTClient --> Timescale[(TimescaleDB)]
  GTFSImporter --> Timescale
  Timescale --> FastAPI[FastAPI Backend]
  FastAPI --> React[React Frontend]

Onboarding Checklist (Day 1):
	•	Clone & Setup: git clone https://github.com/skuduu/Bussikartta.git. Install Python 3.10+ and Node.js (current LTS).
	•	Environment: Create a Python virtualenv. Copy .env.example to .env and set values (DB credentials, MQTT topic/URL, HSL API keys). The React app uses a .env with keys like REACT_APP_API_URL=http://localhost:8000.
	•	TimescaleDB: Start a TimescaleDB/PostgreSQL instance (via Docker Compose or manual install). Enable the TimescaleDB extension.
	•	GTFS Import: Run scripts/import_gtfs.py to load schedule data into the DB. Verify new tables are populated.
	•	MQTT Ingestion: Start the backend service. Confirm that it subscribes to topics like /hfp/v2/journey/#. Test with an MQTT CLI tool.
	•	Launch Services: Run the FastAPI backend and React dev server. Verify the frontend can reach the backend.
	•	Smoke Tests:
	•	GET /api/vehicles and other endpoints return data.
	•	The frontend map shows bus positions and updates.

Code–Feature Mapping Matrix

Feature	Backend (Python)	Frontend (React/TS)
Real-time Vehicle Feed	ingest/mqtt_client.py	–
GTFS Schedule Import	scripts/import_gtfs.py	–
Delay Calculation	services/delay.py	useDelays hook
REST API (Vehicles)	controllers/vehicle_controller.py → services/vehicle.py → models/vehicle.py	useVehicles, <MapView>
REST API (Routes/Stops)	controllers/route_controller.py → services/route.py → models/route.py	useRoutes, <Sidebar>
Interactive Map UI	–	<MapView>, <VehicleMarker>
Sidebar / Info Panel	–	<Sidebar>, <RouteList>
Styling	–	Tailwind CSS

Backend Call Graph:

flowchart LR
    VehicleController[VehicleController] --> VehicleService[VehicleService]
    VehicleService --> VehicleModel[(VehicleModel/TimescaleDB)]
    RouteController[RouteController] --> RouteService[RouteService]
    RouteService --> RouteModel[(RouteModel/TimescaleDB)]

Frontend Component–Hook Graph:

flowchart LR
    MapView["<MapView />"] --> useVehicles["useVehicles() hook"]
    useVehicles --> GETVehicles["GET /api/vehicles"]
    GETVehicles -->|JSON| MapView
    MapView --> useDelays["useDelays() hook"]
    useDelays --> GETDelays["GET /api/delays"]
    GETDelays -->|JSON| MapView
    Sidebar["<Sidebar />"] --> useRoutes["useRoutes() hook"]
    useRoutes --> GETRoutes["GET /api/routes"]
    GETRoutes -->|JSON| Sidebar

Backend Deep-Dive

flowchart LR
    subgraph Ingestion
        GTFS["GTFS Static Files"] -->|Import| TimescaleDB[(TimescaleDB)]
        HFP["HSL MQTT (HFP)"] --> MQTTIngest[MQTTClient Service]
        MQTTIngest -->|Write| TimescaleDB
    end
    TimescaleDB --> FastAPI[FastAPI Backend (Python)]
    FastAPI --> React[React Frontend]

	•	GTFS Pipeline: Parses GTFS CSVs and loads into TimescaleDB. Schedule comparisons used for delay calculations.
	•	MQTT Ingestion: Connects to mqtt.hsl.fi, listens on /hfp/v2/journey/#. Parses and inserts JSON payloads into DB.
	•	Delay Calculation: Computes delay by comparing real-time position vs GTFS stop_times. Results may be stored or calculated dynamically.
	•	Common Issues:
	•	Feed downtime → log-grep for disconnect
	•	Wrong GTFS → mismatch between trip_id in feeds and MQTT
	•	Timezone errors → verify with UTC vs local
	•	Missing indexes or slow inserts → optimize Timescale chunks/indexes

Frontend Status & Integration Guide
	•	Stack: React (TypeScript), Tailwind CSS, MapLibre GL JS, React Query/SWR
	•	Key Components:
	•	<MapView>: Initializes map, renders vehicle layers.
	•	<VehicleMarker>: Shows individual/batch markers.
	•	<Sidebar> / <RouteList>: Route and stop selection.
	•	<VehiclePopup>: Vehicle details.
	•	Hooks:
	•	useVehicles() → /api/vehicles
	•	useRoutes() → /api/routes
	•	useDelays() → /api/delays
	•	Performance:
	•	Cluster markers
	•	Avoid excessive React re-renders
	•	Use memoization
	•	Integration:
	•	.env: REACT_APP_API_URL, etc.
	•	Dev proxy for CORS
	•	API schema expectations documented via Pydantic

Environment & Tooling
	•	.env Variables:

Variable	Example
DB_HOST	localhost
DB_USER, DB_PASS	bussikartta, secret
MQTT_BROKER_URL	mqtt.hsl.fi
MQTT_TOPIC	/hfp/v2/journey/#
REACT_APP_API_URL	http://localhost:8000

	•	Docker Compose:
	•	TimescaleDB
	•	Backend (FastAPI)
	•	(Optional) Frontend
	•	CI/CD:
	•	Lint + test pipeline
	•	Feature flags
	•	Tagging/releases
	•	IDE Setup:
	•	ESLint, Prettier
	•	Mermaid preview plugin
	•	React/TS support

Standards, Testing & Quality Gates
	•	Conventions:
	•	Lint: black, flake8, eslint
	•	Commits: Conventional Commits
	•	Branches: feature/, fix/
	•	Tests:
	•	Python: pytest, tests/
	•	React: jest, @testing-library/react
	•	Coverage & Scanning:
	•	Bandit
	•	Dependabot
	•	pytest-cov

Contribution Playbook
	•	Branch naming: feature/foo-bar, fix/some-bug
	•	Commit messages: feat:, fix:, chore:
	•	PR checklist:
	•	Pass tests
	•	Review checklist complete
	•	Update changelog
	•	Releases:
	•	SemVer tagging: v1.2.3
	•	Auto-changelog

Living Roadmap & Backlog Insights
	•	TODOs:
	•	Story playback (time travel)
	•	Alerts integration (GTFS-Realtime alerts)
	•	Fix edge cases in delay computation
	•	Enhancements:
	•	PWA offline caching
	•	Use Web Workers for delay/map rendering
	•	WebSocket push to frontend
	•	Mobile layout and cluster optimizations