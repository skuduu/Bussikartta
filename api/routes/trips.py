# api/routes/trips.py
from fastapi import APIRouter, HTTPException
import psycopg2
import os

router = APIRouter()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "db"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "hslbussit"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "supersecurepassword"),
    )

@router.get("/trips")
def get_trips():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT trip_id, route_id, service_id, trip_headsign, direction_id FROM trips;")
        rows = cur.fetchall()
        trips = []
        for row in rows:
            trips.append({
                "trip_id": row[0],
                "route_id": row[1],
                "service_id": row[2],
                "trip_headsign": row[3],
                "direction_id": row[4]
            })
        return trips
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()