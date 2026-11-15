<?php

/**
 * Хранилище устройств device-service — собственная база Postgres
 * (отдельная от БД монолита, по паттерну Database per Service).
 */
final class PostgresDeviceRepository implements DeviceRepositoryInterface
{
    private \PDO $pdo;

    /** Поля, которые разрешено редактировать через PATCH, и их колонка в БД */
    private const EDITABLE_FIELDS = [
        'typeId' => 'type_id',
        'houseId' => 'house_id',
        'serialNumber' => 'serial_number',
        'name' => 'name',
        'location' => 'location',
        'status' => 'status',
    ];

    public function __construct(string $dsn, string $user, string $password)
    {
        $this->pdo = new \PDO($dsn, $user, $password, [
            \PDO::ATTR_ERRMODE => \PDO::ERRMODE_EXCEPTION,
        ]);
    }

    public function findAll(): array
    {
        $rows = $this->pdo->query('SELECT * FROM devices ORDER BY created_at DESC')->fetchAll(\PDO::FETCH_ASSOC);

        return array_map([$this, 'hydrate'], $rows);
    }

    public function findById(string $id): ?Device
    {
        $stmt = $this->pdo->prepare('SELECT * FROM devices WHERE id = :id');
        $stmt->execute([':id' => $id]);
        $row = $stmt->fetch(\PDO::FETCH_ASSOC);

        return $row ? $this->hydrate($row) : null;
    }

    public function create(array $attributes): Device
    {
        $id = Uuid::generate();

        $stmt = $this->pdo->prepare(
            'INSERT INTO devices (id, type_id, house_id, serial_number, name, location, status, created_at)
             VALUES (:id, :type_id, :house_id, :serial_number, :name, :location, :status, NOW())'
        );
        $stmt->execute([
            ':id' => $id,
            ':type_id' => $attributes['typeId'],
            ':house_id' => $attributes['houseId'],
            ':serial_number' => $attributes['serialNumber'],
            ':name' => $attributes['name'] ?? null,
            ':location' => $attributes['location'] ?? null,
            ':status' => 'inactive',
        ]);

        return $this->findById($id);
    }

    public function update(string $id, array $attributes): ?Device
    {
        if ($this->findById($id) === null) {
            return null;
        }

        $setClauses = [];
        $params = [':id' => $id];

        foreach (self::EDITABLE_FIELDS as $field => $column) {
            if (array_key_exists($field, $attributes)) {
                $setClauses[] = "$column = :$column";
                $params[":$column"] = $attributes[$field];
            }
        }

        if (empty($setClauses)) {
            return $this->findById($id);
        }

        $sql = 'UPDATE devices SET ' . implode(', ', $setClauses) . ' WHERE id = :id';
        $stmt = $this->pdo->prepare($sql);
        $stmt->execute($params);

        return $this->findById($id);
    }

    private function hydrate(array $row): Device
    {
        return new Device(
            id: $row['id'],
            typeId: $row['type_id'],
            houseId: $row['house_id'],
            serialNumber: $row['serial_number'],
            name: $row['name'],
            location: $row['location'],
            status: $row['status'],
            createdAt: new \DateTimeImmutable($row['created_at']),
        );
    }
}
