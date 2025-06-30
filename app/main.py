import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache import FastAPICache
from redis import asyncio as aioredis

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
    yield


app = FastAPI(
    title="Business Managment System",
    version="0.1.0",
    lifespan=lifespan,
)


app.include_router(tasks_router)
app.include_router(auth_router)
app.include_router(invite_router)
app.include_router(user_router)
app.include_router(department_router)
app.include_router(positions_router)
app.include_router(roles_router)

app.middleware("http")(auth_middleware)

origins = [
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Access-Authorization",
    ],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
