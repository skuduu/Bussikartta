# api/routes/alerts.py
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

@router.get("/alerts")
def get_alerts():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT alert_id, header_text, description_text, active_start, active_end FROM alerts WHERE active_end > NOW();")
        rows = cur.fetchall()
        alerts = []
        for row in rows:
            alerts.append({
                "alert_id": row[0],
                "header_text": row[1],
                "description_text": row[2],
                "active_start": row[3].isoformat() if row[3] else None,
                "active_end": row[4].isoformat() if row[4] else None
            })
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()