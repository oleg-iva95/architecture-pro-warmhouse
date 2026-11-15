<?php

use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;

final class DeviceController
{
    public function __construct(
        private DeviceRepositoryInterface $repository,
        private MonolithClient $monolithClient,
    ) {
    }

    public function list(): JsonResponse
    {
        $own = DeviceView::many($this->repository->findAll());
        $legacy = $this->monolithClient->fetchLegacySensorsAsDevices();

        return new JsonResponse(array_merge($own, $legacy));
    }

    public function create(Request $request): JsonResponse
    {
        $data = json_decode($request->getContent(), true) ?? [];

        if (empty($data['typeId']) || empty($data['houseId']) || empty($data['serialNumber'])) {
            return new JsonResponse([
                'code' => 'INVALID_REQUEST',
                'message' => 'Поля typeId, houseId и serialNumber обязательны',
            ], 400);
        }

        $device = $this->repository->create($data);

        return new JsonResponse(DeviceView::one($device), 201);
    }

    public function show(string $id): JsonResponse
    {
        $device = $this->repository->findById($id);

        if ($device === null) {
            return new JsonResponse(['code' => 'NOT_FOUND', 'message' => 'Устройство не найдено'], 404);
        }

        return new JsonResponse(DeviceView::one($device));
    }

    public function update(Request $request, string $id): JsonResponse
    {
        $data = json_decode($request->getContent(), true) ?? [];

        if (empty($data)) {
            return new JsonResponse([
                'code' => 'INVALID_REQUEST',
                'message' => 'Нужно передать хотя бы одно поле для изменения',
            ], 400);
        }

        $device = $this->repository->update($id, $data);

        if ($device === null) {
            return new JsonResponse(['code' => 'NOT_FOUND', 'message' => 'Устройство не найдено'], 404);
        }

        return new JsonResponse(DeviceView::one($device));
    }
}
