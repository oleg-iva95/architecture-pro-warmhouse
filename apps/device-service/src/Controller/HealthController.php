<?php

use Symfony\Component\HttpFoundation\JsonResponse;

final class HealthController
{
    public function check(): JsonResponse
    {
        return new JsonResponse(['status' => 'ok']);
    }
}
