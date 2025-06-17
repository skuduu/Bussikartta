import os

class IngestionConfig:
    def __init__(self):
        self.db_name = os.getenv("POSTGRES_DB", "hslbussit")
        self.db_user = os.getenv("POSTGRES_USER", "hsluser")
        self.db_password = os.getenv("POSTGRES_PASSWORD", "hslpassword")
        self.db_host = os.getenv("POSTGRES_HOST", "db")
        self.db_port = os.getenv("POSTGRES_PORT", "5432")

    def pg_dsn(self):
        return {
            "dbname": self.db_name,
            "user": self.db_user,
            "password": self.db_password,
            "host": self.db_host,
            "port": self.db_port
        }
