from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "histories_station_observation_system" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "is_current" BOOL NOT NULL  DEFAULT False,
    "changed_at" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "observation_system_id" INT NOT NULL REFERENCES "instruments_observation_systems" ("id") ON DELETE CASCADE,
    "station_id" INT NOT NULL REFERENCES "seismic_station" ("id") ON DELETE CASCADE
);
        CREATE TABLE IF NOT EXISTS "histories_station_position" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "is_current" BOOL NOT NULL  DEFAULT False,
    "changed_at" TIMESTAMPTZ NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "latitude" DOUBLE PRECISION NOT NULL,
    "longitude" DOUBLE PRECISION NOT NULL,
    "elevation" DOUBLE PRECISION,
    "depth" DOUBLE PRECISION,
    "station_id" INT NOT NULL REFERENCES "seismic_station" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "histories_station_observation_system";
        DROP TABLE IF EXISTS "histories_station_position";"""
