from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ingestion.config import IngestionConfig
import psycopg2
import psycopg2.extras

from routes import vehicles, trips, alerts, stops, routes, feed_info, calendar, agency, emissions, fare_attributes, fare_rules, transfers

app = FastAPI()
config = IngestionConfig()

app.include_router(vehicles.router, prefix="/vehicles")
app.include_router(trips.router, prefix="/trips")
app.include_router(alerts.router, prefix="/alerts")
app.include_router(stops.router, prefix="/stops")
app.include_router(routes.router, prefix="/routes")
app.include_router(feed_info.router, prefix="/feed_info")
app.include_router(calendar.router, prefix="/gtfs")
app.include_router(agency.router, prefix="/agency")
app.include_router(emissions.router, prefix="/emissions")
app.include_router(fare_attributes.router, prefix="/fare_attributes")
app.include_router(fare_rules.router, prefix="/fare_rules")
app.include_router(transfers.router, prefix="/transfers")