project_architecture.md

Project Architecture - HSL Bussikartta

⸻

High-level Overview

Project Goal: Real-time and static public transport data ingestion, processing, storage, and serving via API.

Main Tech Stack:
	•	Python
	•	FastAPI
	•	PostgreSQL (TimescaleDB extension)
	•	Docker Compose
	•	MQTT HFP feed
	•	GTFS static & realtime data

Main Components:
	•	api-server — Backend API (FastAPI)
	•	gtfs-static — Imports GTFS static data into PostgreSQL
	•	mqtt-ingest — Ingests live HFP MQTT data
	•	vehicle-ingest — GTFS-RT Realtime ingestion
	•	db — TimescaleDB/PostgreSQL database
	•	backup — Automated DB backups

⸻

Folder Structure (Verified)

hslbussit/repo/
├── api/
│   └── routes/
├── backups/
├── dbdata/
├── docs/
│   ├── project_architecture.md
│   ├── frontend_architecture.md
│   └── gtfs_data_handling.md
├── gtfs_static/
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
├── ingestion/
│   ├── mqtt_hfp_ingest/
│   │   ├── main.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── vehicle_positions_ingest.py
│   ├── config.py
│   └── gtfs_realtime_pb2.py
├── docker-compose.yaml
├── Dockerfile
├── init_timescale.sql
└── backup.sh


⸻

Database Schema (Verified)

Tables
	•	agency
	•	routes
	•	stops
	•	trips
	•	vehicles
	•	vehicle_positions
	•	mqtt_hfp
	•	calendar
	•	emissions
	•	fare_attributes
	•	fare_rules
	•	feed_info
	•	alerts
	•	transfers

⸻

Docker Compose Services (Verified)
	•	api-server
	•	db
	•	backup
	•	gtfs-static
	•	mqtt-ingest
	•	vehicle-ingest

⸻

Backend API Endpoints
	•	/agency
	•	/routes
	•	/stops
	•	/trips
	•	/vehicles
	•	/vehicle_positions
	•	/mqtt_hfp
	•	/calendar
	•	/alerts
	•	/emissions
	•	/fare_attributes
	•	/fare_rules
	•	/feed_info
	•	/transfers

⸻

External APIs Used
	•	GTFS static: HSL
	•	GTFS-RT (realtime): HSL Realtime Feed
	•	MQTT HFP: HSL HFP Feed

⸻

Data Sources

Source	Data Type	Frequency
GTFS static	Schedule, routes, stops	Daily or Weekly
GTFS-RT	Vehicle Positions	Every ~30 sec
MQTT HFP	Vehicle Messages	Live Stream


⸻

Development TODO / Next Phases
	•	✅ Backend architecture functional ✅
	•	⚠ Improve MQTT ingestion error handling
	•	⚠ Add proper tests / CI pipeline
	•	⚠ Start Frontend Architecture implementation
	•	⚠ Improve Docker orchestration
	•	⚠ Add Prometheus/Grafana monitoring

⸻

Notes
	•	Database fully initialized.
	•	All services and containers are operational.
	•	Full end-to-end data ingestion tested.

