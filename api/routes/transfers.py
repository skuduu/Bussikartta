# api/routes/transfers.py
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

@router.get("/transfers")
def get_transfers():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT from_stop_id, to_stop_id, transfer_type, min_transfer_time FROM transfers;")
        rows = cur.fetchall()
        transfers = []
        for row in rows:
            transfers.append({
                "from_stop_id": row[0],
                "to_stop_id": row[1],
                "transfer_type": row[2],
                "min_transfer_time": row[3]
            })
        return transfers
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()