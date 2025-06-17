# api/routes/vehicle_positions.py
from fastapi import APIRouter, HTTPException
import psycopg2
import os
from datetime import datetime

router = APIRouter()

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "db"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "hslbussit"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "supersecurepassword"),
    )

@router.get("/vehicle_positions")
def get_vehicle_positions():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT vehicle_id, latitude, longitude, bearing, speed, timestamp
            FROM vehicle_positions
            ORDER BY timestamp DESC
            LIMIT 100;
        """)
        rows = cur.fetchall()
        positions = []
        for row in rows:
            positions.append({
                "vehicle_id": row[0],
                "latitude": row[1],
                "longitude": row[2],
                "bearing": row[3],
                "speed": row[4],
                "timestamp": row[5].isoformat() if isinstance(row[5], datetime) else row[5]
            })
        return positions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()