import json
import os
import random
import uuid
from datetime import datetime, timezone

import pika
from flask import Flask, request, jsonify

app = Flask(__name__)

LOCATION_BY_SENSOR_ID = {
    "1": "Living Room",
    "2": "Bedroom",
    "3": "Kitchen",
}
SENSOR_ID_BY_LOCATION = {v: k for k, v in LOCATION_BY_SENSOR_ID.items()}

BROKER_URL = os.environ.get("BROKER_URL", "amqp://guest:guest@rabbitmq:5672/%2F")
TELEMETRY_QUEUE = os.environ.get("TELEMETRY_QUEUE", "devices.telemetry.temperature")

# Детерминированный UUID устройства из sensor_id, чтобы одно и то же
# "физическое" устройство всегда давало один и тот же deviceId в событии.
DEVICE_ID_NAMESPACE = uuid.NAMESPACE_DNS


def resolve(location, sensor_id):
    if not location:
        location = LOCATION_BY_SENSOR_ID.get(sensor_id, "Unknown")
    if not sensor_id:
        sensor_id = SENSOR_ID_BY_LOCATION.get(location, "0")
    return location, sensor_id


def random_reading(location, sensor_id):
    location, sensor_id = resolve(location, sensor_id)
    value = round(random.uniform(18.0, 26.0), 1)
    timestamp = datetime.now(timezone.utc)

    reading = {
        "value": value,
        "unit": "C",
        "timestamp": timestamp.isoformat(),
        "location": location,
        "status": "ok",
        "sensor_id": sensor_id,
        "sensor_type": "temperature",
        "description": f"Temperature reading for {location}",
    }

    publish_telemetry_event(sensor_id, value, timestamp)

    return reading


def publish_telemetry_event(sensor_id, value, timestamp):
    """
    Публикует событие в канал devices.telemetry.temperature (AsyncAPI).
    Не должно влиять на синхронный ответ монолиту — если брокер
    недоступен, просто логируем и идём дальше.
    """
    event = {
        "id": str(uuid.uuid4()),
        "deviceId": str(uuid.uuid5(DEVICE_ID_NAMESPACE, f"sensor-{sensor_id}")),
        "metricType": "temperature",
        "value": value,
        "unit": "C",
        "recordedAt": timestamp.isoformat(),
    }

    try:
        connection = pika.BlockingConnection(pika.URLParameters(BROKER_URL))
        channel = connection.channel()
        channel.queue_declare(queue=TELEMETRY_QUEUE, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=TELEMETRY_QUEUE,
            body=json.dumps(event),
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,  # persistent
            ),
        )
        connection.close()
    except Exception as exc:  # брокер недоступен — не роняем HTTP-ответ
        app.logger.warning("Failed to publish telemetry event: %s", exc)


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
