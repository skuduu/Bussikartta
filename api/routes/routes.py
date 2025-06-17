# api/routes/routes.py
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

@router.get("/routes")
def get_routes():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT route_id, route_short_name, route_long_name, route_type FROM routes;")
        rows = cur.fetchall()
        routes = []
        for row in rows:
            routes.append({
                "route_id": row[0],
                "route_short_name": row[1],
                "route_long_name": row[2],
                "route_type": row[3]
            })
        return routes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()