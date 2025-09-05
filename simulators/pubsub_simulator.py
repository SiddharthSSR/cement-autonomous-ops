"""
Synthetic Pub/Sub publisher for cement plant signals.
Requires: pip install google-cloud-pubsub
"""
import json, time, random, datetime
from google.cloud import pubsub_v1

PROJECT = "your-gcp-project"
TOPIC   = "cement-timeseries"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(PROJECT, TOPIC)


def now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


TAGS = [
    ("kiln.main_flame_temp", "C", "KilnMain", 1425, 0.02),
    ("cooler.grate_speed", "Hz", "Cooler1", 8.5, 0.05),
    ("mill1.motor_power", "kW", "RawMill1", 3200, 0.03),
    ("rawmeal.lsf", "", "BlendingSilo", 98.5, 0.01),
]


while True:
    ts = now()
    for tag, unit, eq, base, jitter in TAGS:
        val = base * (1 + random.uniform(-jitter, jitter))
        msg = {
            "ts": ts, "tag": tag, "value": round(val, 2),
            "unit": unit, "equipment": eq, "line": "Line1"
        }
        publisher.publish(topic_path, json.dumps(msg).encode("utf-8"))
    time.sleep(2)

