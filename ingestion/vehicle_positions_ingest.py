import requests
import time
import psycopg2
from google.transit import gtfs_realtime_pb2
import config

GTFS_VEHICLE_URL = config.GTFS_VEHICLE_URL
DB_HOST = config.DB_HOST
DB_PORT = config.DB_PORT
DB_NAME = config.DB_NAME
DB_USER = config.DB_USER
DB_PASS = config.DB_PASS

def fetch_and_store():
    print("Connecting to database...")
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASS
    )
    cur = conn.cursor()
    print("Connected to database.")

    try:
        print("Fetching GTFS realtime feed...")
        response = requests.get(GTFS_VEHICLE_URL)
        response.raise_for_status()
        print("Feed fetched successfully, parsing...")
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        print(f"Parsed feed: {len(feed.entity)} entities")

        for entity in feed.entity:
            if not entity.HasField("vehicle"):
                continue

            vp = entity.vehicle
            vehicle_id = vp.vehicle.id
            route_id = vp.trip.route_id
            lat = vp.position.latitude
            lon = vp.position.longitude
            bearing = vp.position.bearing
            speed = vp.position.speed
            timestamp = vp.timestamp

            cur.execute("""
                INSERT INTO vehicle_positions (vehicle_id, route_id, lat, lon, bearing, speed, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, to_timestamp(%s))
            """, (vehicle_id, route_id, lat, lon, bearing, speed, timestamp))

        conn.commit()
        print("Commit done.")

    except Exception as e:
        print(f"Error during fetch or insert: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    while True:
        fetch_and_store()
        time.sleep(5)