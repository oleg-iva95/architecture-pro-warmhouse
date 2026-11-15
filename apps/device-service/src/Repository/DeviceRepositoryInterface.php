<?php

interface DeviceRepositoryInterface
{
    /** @return Device[] */
    public function findAll(): array;

    public function findById(string $id): ?Device;

    public function create(array $attributes): Device;

    public function update(string $id, array $attributes): ?Device;
}
