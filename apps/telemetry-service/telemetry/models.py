import uuid

from django.db import models


class TelemetryData(models.Model):
    """
    Соответствует сущности TelemetryData из ER-диаграммы:
    id, device_id, metric_type, value, unit, recorded_at.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_id = models.UUIDField()
    metric_type = models.CharField(max_length=50)
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True, null=True)
    recorded_at = models.DateTimeField()

    class Meta:
        db_table = 'telemetry_data'

    def __str__(self):
        return f'{self.metric_type}={self.value}{self.unit or ""} @ {self.device_id}'
