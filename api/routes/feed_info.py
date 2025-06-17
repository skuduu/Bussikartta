# api/routes/feed_info.py
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

@router.get("/feed_info")
def get_feed_info():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT feed_publisher_name, feed_publisher_url, feed_lang, feed_version FROM feed_info;")
        row = cur.fetchone()
        if not row:
            return {}
        return {
            "feed_publisher_name": row[0],
            "feed_publisher_url": row[1],
            "feed_lang": row[2],
            "feed_version": row[3]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()