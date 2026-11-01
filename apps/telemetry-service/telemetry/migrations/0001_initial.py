import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='TelemetryData',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('device_id', models.UUIDField()),
                ('metric_type', models.CharField(max_length=50)),
                ('value', models.FloatField()),
                ('unit', models.CharField(blank=True, max_length=20, null=True)),
                ('recorded_at', models.DateTimeField()),
            ],
            options={
                'db_table': 'telemetry_data',
            },
        ),
        migrations.RunSQL(
            sql=(
                "CREATE INDEX IF NOT EXISTS idx_telemetry_device_id ON telemetry_data(device_id);"
                "CREATE INDEX IF NOT EXISTS idx_telemetry_metric_type ON telemetry_data(metric_type);"
            ),
            reverse_sql=(
                "DROP INDEX IF EXISTS idx_telemetry_device_id;"
                "DROP INDEX IF EXISTS idx_telemetry_metric_type;"
            ),
        ),
    ]
