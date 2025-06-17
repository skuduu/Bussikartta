import os
import json
import ssl
import time
import paho.mqtt.client as mqtt
from sqlalchemy import create_engine, MetaData, Table, Column, String, Float, TIMESTAMP
from sqlalchemy.dialects.postgresql import insert

# DB Config (env based)
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "hslbussit")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "supersecurepassword")

# DB Engine
engine = create_engine(f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
metadata = MetaData()

# Create table definition
mqtt_hfp = Table(
    'mqtt_hfp', metadata,
    Column('tst', TIMESTAMP, primary_key=True),
    Column('veh', String),
    Column('desi', String),
    Column('dir', String),
    Column('lat', Float),
    Column('long', Float),
    Column('spd', Float),
    Column('hdg', Float),
    Column('dl', Float),
    Column('odo', Float),
    Column('route', String),
    Column('oper', String),
)

# Create table if not exists
metadata.create_all(engine)

# MQTT Callback
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload)
        v = payload['VP']
        with engine.begin() as conn:
            stmt = insert(mqtt_hfp).values(
                tst=v['tst'],
                veh=v.get('veh'),
                desi=v.get('desi'),
                dir=v.get('dir'),
                lat=v.get('lat'),
                long=v.get('long'),
                spd=v.get('spd'),
                hdg=v.get('hdg'),
                dl=v.get('dl'),
                odo=v.get('odo'),
                route=v.get('route'),
                oper=v.get('oper'),
            ).on_conflict_do_nothing()
            conn.execute(stmt)
    except Exception as e:
        print(f"Error inserting message: {e}")

# MQTT Client Setup
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.tls_set(cert_reqs=ssl.CERT_REQUIRED)
client.username_pw_set(username="", password="")  # no credentials needed
client.on_message = on_message

# Connect to broker
client.connect("mqtt.hsl.fi", 8883)
client.subscribe("/hfp/v2/journey/ongoing/#")

# Start loop forever
print("🚀 MQTT listener started")
client.loop_forever()
