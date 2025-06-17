from fastapi import APIRouter
from ingestion.config import IngestionConfig
import psycopg2
import psycopg2.extras

router = APIRouter()
config = IngestionConfig()

def get_conn():
    return psycopg2.connect(**config.pg_dsn(), cursor_factory=psycopg2.extras.RealDictCursor)

@router.get("/")
def get_agency():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM gtfs_agency")
    rows = cur.fetchall()
    conn.close()
    return rows