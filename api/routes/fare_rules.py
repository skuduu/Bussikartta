# api/routes/fare_rules.py
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

@router.get("/fare_rules")
def get_fare_rules():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT fare_id, origin_id, destination_id, contains_id FROM fare_rules;")
        rows = cur.fetchall()
        rules = []
        for row in rows:
            rules.append({
                "fare_id": row[0],
                "origin_id": row[1],
                "destination_id": row[2],
                "contains_id": row[3]
            })
        return rules
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()