gtfs_data_handling.md

GTFS Data Handling (early draft)

Status: Early draft — partially implemented

⸻

Components
	•	gtfs-static: handles GTFS static files import into PostgreSQL
	•	vehicle-ingest: handles GTFS-RT (realtime vehicle positions)
	•	mqtt-ingest: handles MQTT HFP feed parsing

⸻

Mapping Notes
	•	Full GTFS static tables created
	•	Some tables still missing full data population (alerts, emissions, etc.)
	•	Parsing logic mostly handled via main.py files in ingestion services
	•	MQTT parsing currently throws ‘VP’ errors (WIP)
	•	Error logs collected for debugging

