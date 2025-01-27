from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "seismic_network" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "code" VARCHAR(5) NOT NULL UNIQUE,
    "name" VARCHAR(20),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS "seismic_station" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "code" VARCHAR(6) NOT NULL,
    "name" VARCHAR(20) NOT NULL,
    "address" VARCHAR(255),
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "network_id" INT NOT NULL REFERENCES "seismic_network" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_seismic_sta_network_3fc647" UNIQUE ("network_id", "code")
);
CREATE TABLE IF NOT EXISTS "seismic_position" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "latitude" DOUBLE PRECISION NOT NULL,
    "longitude" DOUBLE PRECISION NOT NULL,
    "elevation" DOUBLE PRECISION,
    "depth" DOUBLE PRECISION,
    "is_current" BOOL NOT NULL,
    "change_time" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "station_id" INT NOT NULL REFERENCES "seismic_station" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "instruments_data_loggers" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "sampling_rate" DOUBLE PRECISION NOT NULL
);
CREATE TABLE IF NOT EXISTS "instruments_data_logger_instances" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "serial_number" VARCHAR(255) NOT NULL UNIQUE,
    "production_date" DATE NOT NULL,
    "status" VARCHAR(50) NOT NULL,
    "data_logger_id" INT NOT NULL REFERENCES "instruments_data_loggers" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_instruments_serial__36594f" UNIQUE ("serial_number", "data_logger_id")
);
CREATE TABLE IF NOT EXISTS "instruments_integrated_seismometers" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "sampling_rate" DOUBLE PRECISION NOT NULL,
    "sensitivity" DOUBLE PRECISION NOT NULL,
    "firmware_version" VARCHAR(50) NOT NULL
);
CREATE TABLE IF NOT EXISTS "instruments_integrated_seismometer_instances" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "serial_number" VARCHAR(255) NOT NULL UNIQUE,
    "production_date" DATE NOT NULL,
    "status" VARCHAR(50) NOT NULL,
    "integrated_seismometer_id" INT NOT NULL REFERENCES "instruments_integrated_seismometers" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_instruments_serial__e16d53" UNIQUE ("serial_number", "integrated_seismometer_id")
);
CREATE TABLE IF NOT EXISTS "instruments_seismometers" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL,
    "sensitivity" DOUBLE PRECISION NOT NULL
);
CREATE TABLE IF NOT EXISTS "instruments_seismometer_instances" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "serial_number" VARCHAR(255) NOT NULL UNIQUE,
    "production_date" DATE NOT NULL,
    "status" VARCHAR(50) NOT NULL,
    "seismometer_id" INT NOT NULL REFERENCES "instruments_seismometers" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_instruments_serial__2fd396" UNIQUE ("serial_number", "seismometer_id")
);
CREATE TABLE IF NOT EXISTS "instruments_observation_systems" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "data_logger_instance_id" INT REFERENCES "instruments_data_logger_instances" ("id") ON DELETE CASCADE,
    "integrated_seismometer_instance_id" INT REFERENCES "instruments_integrated_seismometer_instances" ("id") ON DELETE CASCADE,
    "seismometer_instance_id" INT REFERENCES "instruments_seismometer_instances" ("id") ON DELETE CASCADE,
    "station_id" INT NOT NULL REFERENCES "seismic_station" ("id") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
