# api/routes/fare_attributes.py
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

@router.get("/fare_attributes")
def get_fare_attributes():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT fare_id, price, currency_type, payment_method FROM fare_attributes;")
        rows = cur.fetchall()
        fares = []
        for row in rows:
            fares.append({
                "fare_id": row[0],
                "price": float(row[1]),
                "currency_type": row[2],
                "payment_method": row[3]
            })
        return fares
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()