<?php

/**
 * Модель устройства — соответствует сущности Device из ER-диаграммы:
 * id, type_id, house_id, serial_number, name, location, status, created_at.
 */
final class Device
{
    public function __construct(
        public readonly string $id,
        public readonly string $typeId,
        public readonly string $houseId,
        public readonly string $serialNumber,
        public readonly ?string $name,
        public readonly ?string $location,
        public readonly string $status,
        public readonly \DateTimeImmutable $createdAt,
    ) {
    }
}
