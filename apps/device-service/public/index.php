<?php

require dirname(__DIR__).'/vendor/autoload.php';

use Symfony\Component\HttpFoundation\JsonResponse;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\Routing\Exception\ResourceNotFoundException;
use Symfony\Component\Routing\Matcher\UrlMatcher;
use Symfony\Component\Routing\RequestContext;
use Symfony\Component\Routing\Route;
use Symfony\Component\Routing\RouteCollection;

// --- Маршруты ---
$routes = new RouteCollection();
$routes->add('health', new Route('/health', ['_controller' => 'health'], [], [], '', [], ['GET']));
$routes->add('devices_list', new Route('/api/v1/devices', ['_controller' => 'devices_list'], [], [], '', [], ['GET']));
$routes->add('devices_create', new Route('/api/v1/devices', ['_controller' => 'devices_create'], [], [], '', [], ['POST']));
$routes->add('devices_get', new Route('/api/v1/devices/{id}', ['_controller' => 'devices_get'], [], [], '', [], ['GET']));
$routes->add('devices_update', new Route('/api/v1/devices/{id}', ['_controller' => 'devices_update'], [], [], '', [], ['PATCH']));

$request = Request::createFromGlobals();
$context = new RequestContext();
$context->fromRequest($request);
$matcher = new UrlMatcher($routes, $context);

// --- Сборка зависимостей (Model + Repository + Infrastructure) ---
$dsn = sprintf(
    'pgsql:host=%s;port=%s;dbname=%s',
    getenv('DEVICE_DB_HOST') ?: 'devices-postgres',
    getenv('DEVICE_DB_PORT') ?: '5432',
    getenv('DEVICE_DB_NAME') ?: 'devices'
);
$repository = new PostgresDeviceRepository(
    $dsn,
    getenv('DEVICE_DB_USER') ?: 'devices',
    getenv('DEVICE_DB_PASSWORD') ?: 'devices'
);
$monolithClient = new MonolithClient(getenv('MONOLITH_URL') ?: 'http://app:8080');

// --- Controller'ы ---
$deviceController = new DeviceController($repository, $monolithClient);
$healthController = new HealthController();

// --- Диспетчеризация запроса в контроллер ---
try {
    $parameters = $matcher->match($request->getPathInfo());

    $response = match ($parameters['_controller']) {
        'health' => $healthController->check(),
        'devices_list' => $deviceController->list(),
        'devices_create' => $deviceController->create($request),
        'devices_get' => $deviceController->show($parameters['id']),
        'devices_update' => $deviceController->update($request, $parameters['id']),
        default => new JsonResponse(['code' => 'NOT_FOUND', 'message' => 'Маршрут не найден'], 404),
    };
} catch (ResourceNotFoundException $e) {
    $response = new JsonResponse(['code' => 'NOT_FOUND', 'message' => 'Маршрут не найден'], 404);
} catch (\Throwable $e) {
    $response = new JsonResponse(['code' => 'INTERNAL_ERROR', 'message' => $e->getMessage()], 500);
}

$response->send();
