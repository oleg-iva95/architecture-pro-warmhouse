<?php

/**
 * Клиент к старому монолиту (smarthome-app).
 * Нужен на время миграции: показывает единым списком и новые устройства
 * (из этого сервиса), и ещё не перенесённые из монолита (Strangler Fig).
 */
final class MonolithClient
{
    public function __construct(private string $baseUrl)
    {
    }

    public function fetchLegacySensorsAsDevices(): array
    {
        $context = stream_context_create(['http' => ['timeout' => 2]]);
        $raw = @file_get_contents(rtrim($this->baseUrl, '/') . '/api/v1/sensors', false, $context);

        if ($raw === false) {
            return [];
        }

        $sensors = json_decode($raw, true);
        if (!is_array($sensors)) {
            return [];
        }

        return array_map(static function (array $sensor) {
            return [
                'id' => (string) ($sensor['id'] ?? ''),
                'typeId' => $sensor['type'] ?? null,
                'houseId' => null,
                'serialNumber' => null,
                'name' => $sensor['name'] ?? null,
                'location' => $sensor['location'] ?? null,
                'status' => $sensor['status'] ?? null,
                'createdAt' => $sensor['created_at'] ?? null,
                'source' => 'monolith (legacy)',
            ];
        }, $sensors);
    }
}
