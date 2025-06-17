README.md

HSL Bussikartta

⸻

Quick Start

docker-compose up --build

Backend API (FastAPI)

Runs on: http://localhost:8007

Endpoint	Purpose
/agency	Agency info
/routes	Routes
/stops	Stops
/trips	Trips
/vehicles	Vehicles
/vehicle_positions	Vehicle Positions
/mqtt_hfp	MQTT HFP data
/calendar	Calendar data
/alerts	Service alerts
/emissions	Emissions data
/fare_attributes	Fare Attributes
/fare_rules	Fare Rules
/feed_info	Feed Info
/transfers	Transfers

Docker Services

Service	Description
api-server	Backend API
gtfs-static	GTFS Static Importer
mqtt-ingest	MQTT Ingestion
vehicle-ingest	GTFS-RT Realtime Ingest
db	TimescaleDB
backup	DB Backup

Database Connection (Internal)
	•	host: db
	•	db: hslbussit
	•	user: postgres
	•	pw: supersecurepassword

⸻

GTFS Sources
	•	HSL GTFS Static: https://dev.hsl.fi/gtfs/hsl.zip
	•	HSL Realtime: https://digitransit.fi/en/developers/apis/gtfs-realtime/
	•	HSL MQTT HFP: Requires credentials

⸻

Work In Progress
	•	⚠ MQTT parser bug with ‘VP’ message
	•	⚠ Web frontend not yet implemented