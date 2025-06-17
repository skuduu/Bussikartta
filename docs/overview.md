# Bussikartta

**Bussikartta** is a real-time public transport tracking system that combines live vehicle location data with scheduled timetable information. It provides a map-based view of buses (and other transit vehicles) and highlights how late or on-time they are running compared to their schedule. The project includes a backend for data ingestion and an API, and a planned frontend for visualization.

## Overview

Bussikartta’s goal is to show the current positions of transit vehicles and their delays in an interactive map. It focuses on the Helsinki region (HSL) and can be extended to other regions. The system uses **FastAPI** (Python) for the backend API, **TimescaleDB** (an extension of PostgreSQL) for time-series data storage, and plans to use a **React** + **Tailwind CSS** + **MapLibre GL JS** frontend for the map UI. Real-time vehicle locations are obtained from an **MQTT** feed provided by the transit authority, and static schedule data comes from **GTFS** (General Transit Feed Specification) files.

**Key features:**

- **Real-time Vehicle Tracking:** Subscribes to HSL’s high-frequency positioning feed to get live updates of bus locations (with support for other cities' feeds in the future)【46†L71-L78】【29†L23-L31】. Vehicles are displayed on a map with their current coordinates.
- **Delay Monitoring:** Cross-references real-time data with GTFS schedule data to calculate how many minutes late each bus or tram is running. Delays are updated continuously, allowing identification of late vehicles.
- **Historical Data Storage:** Uses TimescaleDB to store incoming vehicle position data as a time-series. This enables querying historical trajectories or performing analyses (e.g., performance over time) while handling high insert rates efficiently【50†L315-L323】.
- **RESTful API:** Exposes endpoints to fetch vehicle positions, routes, stops, and delay information for use by the frontend or other clients. The API is documented and provides structured JSON responses.
- **Planned Frontend:** A responsive web application (React + Tailwind) will visualize vehicles on an interactive MapLibre map. Users will be able to filter by route or stop and see details like vehicle identifiers, routes, and delay status.
- **Scalability and Performance:** The system is designed for high-frequency data. TimescaleDB (built on PostgreSQL) ensures scalable time-series storage and fast queries, while FastAPI provides high-performance async I/O for the API【50†L315-L323】. Data ingestion and serving are decoupled for stability.

## Repository Structure

The repository is structured to separate concerns clearly:

- **`backend/` (FastAPI application)** – Python code for the API server and data ingestion. This includes route definitions, database models, and MQTT client logic.
- **`frontend/` (React app)** – *(Planned)* The React application source (if included or to be added) using Tailwind and MapLibre for the UI.
- **`data/`** – Any sample data or scripts for loading data (e.g. GTFS static files or processing scripts).
- **`docs/`** – Documentation files for developers (architecture, data handling, API reference, deployment, etc.).
- **`docker-compose.yml`** – Docker Compose configuration to run the database, backend, and other services for deployment.
- **`backup.sh`** – Utility script for backing up the TimescaleDB database (dumps the data for safe-keeping).
- **Configuration files** – e.g. `.env.example` for environment variables, etc., to configure database connection or API settings.

*(Note: The actual structure and file names might differ; see the repository for the exact layout.)*

## Quickstart

Follow these steps to get Bussikartta up and running quickly:

1. **Clone the Repository:**  
   ```bash
   git clone https://github.com/skuduu/Bussikartta.git
   cd Bussikartta
   ```

2. **Configure Environment:**  
   Copy or create an `.env` file (if provided, e.g. `env.example`) and set required environment variables. At minimum, set database credentials if needed (or use the defaults in the Docker setup):
   - `DB_HOST`, `DB_PORT` – TimescaleDB host (and port, default 5432).
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD` – Database name, username, and password (matching what the Timescale container expects).
   - `MQTT_BROKER_URL` – MQTT broker for real-time data (default is the public HSL broker `mqtt.hsl.fi` on port 1883)【29†L23-L31】.
   - `MQTT_TOPIC` – Topic pattern for subscriptions (default `"/hfp/journey/#"` to receive all vehicle position messages)【29†L31-L35】.
   - Other settings like `API_PORT` or `DEBUG` as needed.

3. **Launch Services with Docker:**  
   Ensure Docker and Docker Compose are installed. Then run:  
   ```bash
   docker-compose up -d
   ```  
   This will start the TimescaleDB database service and the FastAPI backend service (and possibly other services defined, such as a message broker or ingestion service if applicable). The first time you run this, the backend may also initiate a GTFS static data import if configured to do so.

4. **Initialize GTFS Data:**  
   If the GTFS static schedule data is not automatically loaded on startup, run the import step manually:  
   ```bash
   docker-compose exec backend python scripts/import_gtfs.py
   ```  
   (Replace with the actual path/command if different.)  
   This step downloads the latest GTFS zip (or uses a provided file) and loads routes, stops, trips, and timetables into the database. **Note:** You can skip this if the backend already did it or if using a pre-loaded database.

5. **Access the API:**  
   Once up, the FastAPI backend will be listening (by default on port 8000). You can access the interactive API documentation by opening **`http://localhost:8000/docs`** in a browser. This Swagger/OpenAPI UI lists all endpoints and allows trying them out. For example, try GET `http://localhost:8000/api/vehicles` to fetch current vehicle data.

6. **Run the Frontend (optional/planned):**  
   If a frontend React app is included or once it’s built, you can start it separately (e.g., `npm install` then `npm start` if it’s a standard Create React App). Configure the frontend to point to the backend API (e.g. base URL `http://localhost:8000/api`). The default development server runs on port 3000. Open **`http://localhost:3000`** to view the app. *(If the frontend is not yet implemented in the repo, skip this step.)*

7. **Monitor and Enjoy:**  
   With backend (and frontend) running, you should see live bus locations being ingested. The API will continuously update as MQTT messages stream in. If you query the API for vehicles, you’ll get data including positions and delay information. On the map UI (if running), you’ll see moving markers for each bus, color-coded or annotated to indicate lateness.

## Documentation

For detailed technical information, please refer to the [**docs/**](docs/) folder:

- **[Project Architecture](docs/project_architecture.md):** Deep dive into backend components, data flow, database schema, and design principles.
- **[GTFS Data Handling](docs/gtfs_data_handling.md):** How GTFS static schedule data is parsed and kept updated, and how it ties into real-time info.
- **[Frontend Architecture](docs/frontend_architecture.md):** Outline of the planned frontend technology stack, map rendering strategy, and how the client interacts with the API.
- **[API Reference](docs/api_reference.md):** Full list of API endpoints with methods, parameters, and example responses (grouped by vehicles, routes, stops, etc.).
- **[Deployment Guide](docs/deployment.md):** Instructions for deploying the system in different environments (Docker Compose usage, environment config, updating data, backups, and scaling).

---

Feel free to contribute or open issues. We welcome improvements from the community. Happy coding and happy commuting!

---

## Quick Links

- **Live Demo:** *Coming soon or URL if deployed*  
- **License:** MIT (or specify license here)  
- **Contact:** (e.g., maintainers or project email)

---

*Bussikartta combines open transit data and modern tech to bring real-time public transport insights to developers and commuters alike.*


