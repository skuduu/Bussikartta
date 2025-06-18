import os
import psycopg2
from fastapi import APIRouter

router = APIRouter()

DB_HOST = os.getenv("PGHOST", "db")
DB_PORT = os.getenv("PGPORT", "5432")
DB_NAME = os.getenv("PGDATABASE", "hslbussit")
DB_USER = os.getenv("PGUSER", "postgres")
DB_PASS = os.getenv("PGPASSWORD", "supersecurepassword")

@router.get("/vehicles")
def get_vehicles():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS
    )
    cur = conn.cursor()
    cur.execute("""
    SELECT
      veh       AS vehicle_id,
      desi      AS label,
      lat,
      long      AS lon,
      spd       AS speed,
      tst       AS timestamp
    FROM (
      SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY veh ORDER BY tst DESC) AS rn
      FROM mqtt_hfp
    ) sub
    WHERE rn = 1;
    """)
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    result = [dict(zip(cols, row)) for row in rows]
    cur.close()
    conn.close()
    return result
