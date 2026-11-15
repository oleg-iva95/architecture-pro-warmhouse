from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TelemetryData
from .serializers import TelemetryDataSerializer


class HealthView(APIView):
    def get(self, request):
        return Response({'status': 'ok'})


class TelemetryListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/telemetry            — список показаний
    GET  /api/v1/telemetry?deviceId=  — показания конкретного устройства
    POST /api/v1/telemetry            — новое показание
    """

    serializer_class = TelemetryDataSerializer

    def get_queryset(self):
        queryset = TelemetryData.objects.all().order_by('-recorded_at')

        device_id = self.request.query_params.get('deviceId')
        if device_id:
            queryset = queryset.filter(device_id=device_id)

        metric_type = self.request.query_params.get('metricType')
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)

        return queryset


class TelemetryDetailView(generics.RetrieveAPIView):
    """GET /api/v1/telemetry/{id} — одно показание"""

    serializer_class = TelemetryDataSerializer
    queryset = TelemetryData.objects.all()
    lookup_field = 'id'
