-- Таблица устройств device-service (своя БД, отдельная от монолита).
-- Названия и типы колонок соответствуют сущности Device из ER-диаграммы.
CREATE TABLE IF NOT EXISTS devices (
    id UUID PRIMARY KEY,
    type_id VARCHAR(50) NOT NULL,
    house_id UUID NOT NULL,
    serial_number VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(100),
    location VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'inactive',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_devices_house_id ON devices(house_id);
CREATE INDEX IF NOT EXISTS idx_devices_type_id ON devices(type_id);
