import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv("PGHOST", "repo-db-1"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "hslbussit"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", "your_db_password")
    )
    return conn