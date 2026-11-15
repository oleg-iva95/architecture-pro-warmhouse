from django.urls import path

from .views import HealthView, TelemetryDetailView, TelemetryListCreateView

urlpatterns = [
    path('health', HealthView.as_view()),
    path('api/v1/telemetry', TelemetryListCreateView.as_view()),
    path('api/v1/telemetry/<uuid:id>', TelemetryDetailView.as_view()),
]
