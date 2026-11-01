from flask import Flask, request, jsonify
import random
from datetime import datetime, timezone

app = Flask(__name__)

LOCATION_BY_SENSOR_ID = {
    "1": "Living Room",
    "2": "Bedroom",
    "3": "Kitchen",
}
SENSOR_ID_BY_LOCATION = {v: k for k, v in LOCATION_BY_SENSOR_ID.items()}


def resolve(location, sensor_id):
    if not location:
        location = LOCATION_BY_SENSOR_ID.get(sensor_id, "Unknown")
    if not sensor_id:
        sensor_id = SENSOR_ID_BY_LOCATION.get(location, "0")
    return location, sensor_id


def random_reading(location, sensor_id):
    location, sensor_id = resolve(location, sensor_id)
    return {
        "value": round(random.uniform(18.0, 26.0), 1),
        "unit": "C",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "location": location,
        "status": "ok",
        "sensor_id": sensor_id,
        "sensor_type": "temperature",
        "description": f"Temperature reading for {location}",
    }


@app.route("/temperature")
def temperature_by_location():
    location = request.args.get("location", "")
    return jsonify(random_reading(location, ""))


@app.route("/temperature/<sensor_id>")
def temperature_by_sensor(sensor_id):
    return jsonify(random_reading("", sensor_id))


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
