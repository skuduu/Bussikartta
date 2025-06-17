# api/routes/calendar.py
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

@router.get("/calendar")
def get_calendar():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT service_id, monday, tuesday, wednesday, thursday, friday, saturday, sunday, start_date, end_date
            FROM calendar;
        """)
        rows = cur.fetchall()
        calendar = []
        for row in rows:
            calendar.append({
                "service_id": row[0],
                "monday": row[1],
                "tuesday": row[2],
                "wednesday": row[3],
                "thursday": row[4],
                "friday": row[5],
                "saturday": row[6],
                "sunday": row[7],
                "start_date": row[8].isoformat() if row[8] else None,
                "end_date": row[9].isoformat() if row[9] else None,
            })
        return calendar
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()