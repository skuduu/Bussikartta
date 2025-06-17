# api/routes/stops.py
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

@router.get("/stops")
def get_stops():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT stop_id, stop_name, stop_lat, stop_lon FROM stops;")
        rows = cur.fetchall()
        stops = []
        for row in rows:
            stops.append({
                "stop_id": row[0],
                "stop_name": row[1],
                "stop_lat": row[2],
                "stop_lon": row[3]
            })
        return stops
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()