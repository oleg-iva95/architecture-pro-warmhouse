from django.utils import timezone
from rest_framework import serializers

from .models import TelemetryData


class TelemetryDataSerializer(serializers.ModelSerializer):
    """
    Поля в БД — snake_case, как в ER-диаграмме (device_id, metric_type,
    recorded_at). В JSON наружу отдаём camelCase, как в остальных
    сервисах (deviceId, metricType, recordedAt).
    """

    deviceId = serializers.UUIDField(source='device_id')
    metricType = serializers.CharField(source='metric_type')
    recordedAt = serializers.DateTimeField(source='recorded_at', required=False)

    class Meta:
        model = TelemetryData
        fields = ['id', 'deviceId', 'metricType', 'value', 'unit', 'recordedAt']
        read_only_fields = ['id']

    def create(self, validated_data):
        validated_data.setdefault('recorded_at', timezone.now())
        return super().create(validated_data)
