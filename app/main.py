import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis.asyncio import Redis

from app.auth.middleware import auth_middleware
from app.config import settings
from app.routers.v1.tasks import tasks_router
from app.routers.v1.auth import auth_router
from app.routers.v1.invites import invite_router
from app.routers.v1.users import user_router
from app.routers.v1.departments import department_router
from app.routers.v1.positions import positions_router
from app.routers.v1.roles import roles_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Инициализация и корректное закрытие подключения к Redis."""
    redis: Redis = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        encoding="utf-8",
        decode_responses=True,
    )
    try:
        FastAPICache.init(
            RedisBackend(redis),
            prefix=settings.CACHE_PREFIX,
        )
        yield
    finally:
        await redis.close()


middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
        allow_headers=[
            "Content-Type",
            "Set-Cookie",
            "Access-Control-Allow-Headers",
            "Access-Control-Allow-Origin",
            "Access-Authorization",
        ],
    ),
    Middleware(auth_middleware),  # убедитесь, что auth_middleware реализует ASGI‑сигнатуру
]

app = FastAPI(
    title="Business Management System",
    version="0.1.0",
    lifespan=lifespan,
    middleware=middleware,
)

API_PREFIX = "/v1"

# роутеры подключаются под общим префиксом версии
app.include_router(tasks_router, prefix=API_PREFIX)
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(invite_router, prefix=API_PREFIX)
app.include_router(user_router, prefix=API_PREFIX)
app.include_router(department_router, prefix=API_PREFIX)
app.include_router(positions_router, prefix=API_PREFIX)
app.include_router(roles_router, prefix=API_PREFIX)

# ---- Локальный запуск (только для разработки) ----
# В продакшене приложение запускается командой:
#   uvicorn app.main:app --host 0.0.0.0 --port 8000
# --------------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
