from tortoise.contrib.fastapi import RegisterTortoise
from app.config import TORTOISE_ORM


def init_db(app):
    RegisterTortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=True,
        add_exception_handlers=True,
    )
