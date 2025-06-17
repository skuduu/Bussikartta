import os
import zipfile
import requests
import psycopg2
import pandas as pd
from io import BytesIO

GTFS_URL = "https://infopalvelut.storage.hsldev.com/gtfs/hsl.zip"

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "hslbussit")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "supersecurepassword")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS
    )

def download_gtfs():
    print("Downloading GTFS...")
    r = requests.get(GTFS_URL)
    r.raise_for_status()
    return BytesIO(r.content)

def extract_gtfs(zip_data):
    print("Extracting files...")
    with zipfile.ZipFile(zip_data) as z:
        z.extractall("/tmp/gtfs_static")

def create_tables():
    with get_db_connection() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS agency (
                agency_id TEXT PRIMARY KEY,
                agency_name TEXT,
                agency_url TEXT,
                agency_timezone TEXT
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS stops (
                stop_id TEXT PRIMARY KEY,
                stop_name TEXT,
                stop_lat DOUBLE PRECISION,
                stop_lon DOUBLE PRECISION
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS routes (
                route_id TEXT PRIMARY KEY,
                route_short_name TEXT,
                route_long_name TEXT,
                route_type INTEGER
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                trip_id TEXT PRIMARY KEY,
                route_id TEXT,
                service_id TEXT,
                trip_headsign TEXT,
                direction_id INTEGER
            );
        """)
        conn.commit()

def load_data():
    with get_db_connection() as conn:
        cur = conn.cursor()

        agency = pd.read_csv("/tmp/gtfs_static/agency.txt")
        for _, row in agency.iterrows():
            cur.execute("""
                INSERT INTO agency (agency_id, agency_name, agency_url, agency_timezone)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (agency_id) DO UPDATE SET agency_name=EXCLUDED.agency_name
            """, (row['agency_id'], row['agency_name'], row['agency_url'], row['agency_timezone']))

        stops = pd.read_csv("/tmp/gtfs_static/stops.txt")
        for _, row in stops.iterrows():
            cur.execute("""
                INSERT INTO stops (stop_id, stop_name, stop_lat, stop_lon)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (stop_id) DO UPDATE SET stop_name=EXCLUDED.stop_name
            """, (row['stop_id'], row['stop_name'], row['stop_lat'], row['stop_lon']))

        routes = pd.read_csv("/tmp/gtfs_static/routes.txt")
        for _, row in routes.iterrows():
            cur.execute("""
                INSERT INTO routes (route_id, route_short_name, route_long_name, route_type)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (route_id) DO UPDATE SET route_short_name=EXCLUDED.route_short_name
            """, (row['route_id'], row['route_short_name'], row['route_long_name'], row['route_type']))

        trips = pd.read_csv("/tmp/gtfs_static/trips.txt")
        for _, row in trips.iterrows():
            cur.execute("""
                INSERT INTO trips (trip_id, route_id, service_id, trip_headsign, direction_id)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (trip_id) DO UPDATE SET trip_headsign=EXCLUDED.trip_headsign
            """, (row['trip_id'], row['route_id'], row['service_id'], row['trip_headsign'], row['direction_id']))

        conn.commit()

if __name__ == "__main__":
    zip_data = download_gtfs()
    extract_gtfs(zip_data)
    create_tables()
    load_data()
    print("✅ GTFS static import done.")
