from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "seismic_position" ADD "is_virtual" BOOL NOT NULL  DEFAULT False;
        ALTER TABLE "histories_station_position" ADD "is_virtual" BOOL NOT NULL  DEFAULT False;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "seismic_position" DROP COLUMN "is_virtual";
        ALTER TABLE "histories_station_position" DROP COLUMN "is_virtual";"""
