from os import environ
from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = environ.get("PROJECT_NAME", "Seismic API")
    PROJECT_DESCRIPTION: str = environ.get(
        "PROJECT_DESCRIPTION", "API for seismic data management"
    )
    VERSION: str = environ.get("VERSION", "0.1.0")
    DEBUG: bool = environ.get("DEBUG", False)
    TEST: bool = environ.get("TEST", False)

    DB_HOST: str = environ.get("DB_HOST", "127.0.0.1")
    DB_PORT: int = environ.get("DB_PORT", 5432)
    DB_USER: str = environ.get("DB_USER", "postgres")
    DB_PASSWORD: str = environ.get("DB_PASSWORD", "postgres")
    DB_NAME: str = environ.get("DB_NAME", "seismic")
    DB_TEST_NAME: str = environ.get("DB_TEST_NAME", "mytest")
    DB_POOL_MAX: int = environ.get("DB_POOL_MAX", 20)
    DB_POOL_CONN_LIFE: int = environ.get("DB_POOL_CONN_LIFE", 600)
    TIMEZONE: str = environ.get("TIMEZONE", "Asia/Shanghai")

    TORTOISE_ORM: dict = {
        "connections": {
            "default": {
                # 使用postgresql数据库
                "engine": "tortoise.backends.asyncpg",
                # 从环境变量中读取
                "credentials": {
                    "host": DB_HOST,
                    "port": DB_PORT,
                    "user": DB_USER,
                    "password": DB_PASSWORD,
                    "database": DB_NAME,
                    "maxsize": DB_POOL_MAX,
                    # "connection_lifetime": DB_POOL_CONN_LIFE,
                },
            }
        },
        "apps": {
            "models": {
                "models": [
                    "app.models.seismic",
                    "app.models.instruments",
                    "aerich.models",
                ],
                "default_connection": "default",
            }
        },
        "use_tz": True,
        "timezone": "Asia/Shanghai",
    }

    TORTOISE_TEST_ORM: dict = {
        "connections": {
            "test": {
                # 使用postgresql数据库
                "engine": "tortoise.backends.asyncpg",
                # 从环境变量中读取
                "credentials": {
                    "host": DB_HOST,
                    "port": DB_PORT,
                    "user": DB_USER,
                    "password": DB_PASSWORD,
                    "database": DB_TEST_NAME,
                    "maxsize": DB_POOL_MAX,
                    # "connection_lifetime": DB_POOL_CONN_LIFE,
                },
            }
        },
        "apps": {
            "models": {
                "models": [
                    "app.models.seismic",
                    "app.models.instruments",
                    "aerich.models",
                ],
                "default_connection": "test",
            }
        },
        "use_tz": True,
        "timezone": "Asia/Shanghai",
    }

    model_config = ConfigDict(
        env_file_encoding="utf-8", env_file=".env", case_sensitive=True
    )


settings = Settings()


TORTOISE_ORM = settings.TORTOISE_ORM
TORTOISE_TEST_ORM = settings.TORTOISE_TEST_ORM
