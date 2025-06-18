import os
import json
import time
import logging
import psycopg2
import paho.mqtt.client as mqtt
from datetime import datetime

# Environment variables
MQTT_BROKER = os.getenv("MQTT_BROKER", "mqtt.hsl.fi")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "/hfp/v2/journey/ongoing/vp/bus/#")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "hslbussit")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "supersecurepassword")

# Setup logging
logfile_path = "/var/log/mqtt_ingest.log"
os.makedirs(os.path.dirname(logfile_path), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(logfile_path),
        logging.StreamHandler()
    ]
)

def log(msg): logging.info(msg)

# MQTT event callbacks
def on_connect(client, userdata, flags, rc):
    log(f"Connected to MQTT broker {MQTT_BROKER}:{MQTT_PORT} with result code {rc}")
    client.subscribe(MQTT_TOPIC)
    log(f"Subscribed to topic: {MQTT_TOPIC}")

def on_message(client, userdata, msg):
    log("🔔 Message received")
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        log(f"🔍 Raw payload: {msg.payload[:80]}...")

        vp = payload.get("VP", {})
        if not vp:
            log("⚠️  No 'VP' key, skipping insert")
            return

        record = {
            "desi": vp.get("desi"),
            "dir": vp.get("dir"),
            "oper": vp.get("oper"),
            "veh": vp.get("veh"),
            "tst": vp.get("tst"),
            "tsi": vp.get("tsi"),
            "spd": vp.get("spd"),
            "hdg": vp.get("hdg"),
            "lat": vp.get("lat"),
            "long": vp.get("long"),
            "acc": vp.get("acc"),
            "dl": vp.get("dl"),
            "odo": vp.get("odo"),
            "drst": vp.get("drst"),
            "oday": vp.get("oday"),
            "jrn": vp.get("jrn"),
            "line": vp.get("line"),
            "start": vp.get("start"),
            "loc": vp.get("loc"),
            "stop": vp.get("stop"),
            "route": vp.get("route"),
            "occu": vp.get("occu"),
        }

        log(f"✅ Inserting record for veh={record['veh']} tst={record['tst']}")

        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
        )
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO mqtt_hfp (desi, dir, oper, veh, tst, tsi, spd, hdg, lat, long, acc,
                                  dl, odo, drst, oday, jrn, line, start, loc, stop, route, occu)
            VALUES (%(desi)s, %(dir)s, %(oper)s, %(veh)s, %(tst)s, %(tsi)s, %(spd)s, %(hdg)s,
                    %(lat)s, %(long)s, %(acc)s, %(dl)s, %(odo)s, %(drst)s, %(oday)s, %(jrn)s,
                    %(line)s, %(start)s, %(loc)s, %(stop)s, %(route)s, %(occu)s)
        """, record)
        conn.commit()
        cur.close()
        conn.close()

        log("✔️ Insert successful")

    except Exception as e:
        log(f"❌ Error inserting message: {str(e)}")

# MQTT setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

log("🚀 Starting MQTT client loop")
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_forever()