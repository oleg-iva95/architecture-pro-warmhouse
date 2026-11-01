<?php

/**
 * "View"-слой: превращает модель Device в JSON-представление ответа API.
 * Отделён от контроллера, чтобы формат ответа не был размазан по бизнес-логике.
 */
final class DeviceView
{
    public static function one(Device $device): array
    {
        return [
            'id' => $device->id,
            'typeId' => $device->typeId,
            'houseId' => $device->houseId,
            'serialNumber' => $device->serialNumber,
            'name' => $device->name,
            'location' => $device->location,
            'status' => $device->status,
            'createdAt' => $device->createdAt->format(DATE_ATOM),
            'source' => 'device-service',
        ];
    }

    /** @param Device[] $devices */
    public static function many(array $devices): array
    {
        return array_map([self::class, 'one'], $devices);
    }
}
