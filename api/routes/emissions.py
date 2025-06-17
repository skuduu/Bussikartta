# api/routes/emissions.py
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

@router.get("/emissions")
def get_emissions():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT vehicle_id, emission_type, emission_value FROM emissions;")
        rows = cur.fetchall()
        emissions = []
        for row in rows:
            emissions.append({
                "vehicle_id": row[0],
                "emission_type": row[1],
                "emission_value": row[2]
            })
        return emissions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()