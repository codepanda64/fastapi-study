from contextlib import asynccontextmanager
from fastapi import FastAPI

from tortoise import Tortoise
from tortoise.contrib.fastapi import RegisterTortoise

# from app.db import init_db
from app.config import settings, TORTOISE_ORM
from app.api import seismic


import pydantic

print(pydantic.__version__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 初始化 Tortoise ORM
    register_tortoise = RegisterTortoise(app, config=TORTOISE_ORM)
    await register_tortoise.init_orm()
    yield
    # 关闭 Tortoise ORM 连接
    await register_tortoise.close_orm()
    # await Tortoise.init(config=TORTOISE_ORM)
    # yield
    # # 关闭 Tortoise ORM 连接
    # await Tortoise.close_connections()


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )

    # register_tortoise(
    #     application,
    #     config=TORTOISE_ORM,
    #     generate_schemas=True,
    #     add_exception_handlers=True,
    # )

    application.include_router(seismic.router, prefix="/api")

    return application


app = get_application()

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # 启动时初始化数据库
#     init_db(app)
#     yield  # 应用运行期间
#     # 关闭时清理资源（如果需要）
#     await Tortoise.close_connections()


# app = FastAPI(lifespan=lifespan)


# 其他路由和逻辑
@app.get("/")
async def root():
    return {"message": "Hello World"}
