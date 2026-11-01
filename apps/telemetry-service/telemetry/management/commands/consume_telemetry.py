import json
import os
import time

import pika
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from telemetry.models import TelemetryData


class Command(BaseCommand):
    help = "Слушает канал devices.telemetry.temperature и сохраняет показания в БД"

    def handle(self, *args, **options):
        broker_url = os.environ.get("BROKER_URL", "amqp://guest:guest@rabbitmq:5672/%2F")
        queue_name = os.environ.get("TELEMETRY_QUEUE", "devices.telemetry.temperature")

        connection = self._connect_with_retry(broker_url)
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_qos(prefetch_count=1)

        def callback(ch, method, properties, body):
            try:
                payload = json.loads(body)
                recorded_at = payload.get("recordedAt")

                TelemetryData.objects.create(
                    id=payload["id"],
                    device_id=payload["deviceId"],
                    metric_type=payload.get("metricType", "temperature"),
                    value=payload["value"],
                    unit=payload.get("unit"),
                    recorded_at=parse_datetime(recorded_at) if recorded_at else timezone.now(),
                )

                self.stdout.write(self.style.SUCCESS(f"Saved reading {payload['id']}"))
                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as exc:
                self.stderr.write(self.style.ERROR(f"Failed to process message: {exc}"))
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

        channel.basic_consume(queue=queue_name, on_message_callback=callback)

        self.stdout.write(self.style.SUCCESS(f"Listening on queue '{queue_name}'..."))

        while True:
            try:
                channel.start_consuming()
            except pika.exceptions.AMQPConnectionError:
                self.stderr.write(self.style.WARNING("Connection to RabbitMQ lost, reconnecting..."))
                connection = self._connect_with_retry(broker_url)
                channel = connection.channel()
                channel.queue_declare(queue=queue_name, durable=True)
                channel.basic_qos(prefetch_count=1)
                channel.basic_consume(queue=queue_name, on_message_callback=callback)

    def _connect_with_retry(self, broker_url, max_attempts=10, delay_seconds=3):
        """
        RabbitMQ healthcheck в docker-compose может позеленеть чуть раньше,
        чем сервис полностью готов принимать AMQP-соединения. Поэтому
        пробуем подключиться несколько раз с паузой, а не падаем с первой
        попытки (сами перезапуски контейнера через restart-policy — это
        слишком медленный и шумный способ дождаться брокера).
        """
        last_error = None
        for attempt in range(1, max_attempts + 1):
            try:
                return pika.BlockingConnection(pika.URLParameters(broker_url))
            except pika.exceptions.AMQPConnectionError as exc:
                last_error = exc
                self.stderr.write(
                    self.style.WARNING(
                        f"RabbitMQ недоступен (попытка {attempt}/{max_attempts}): {exc}. "
                        f"Повтор через {delay_seconds} сек."
                    )
                )
                time.sleep(delay_seconds)

        raise last_error
