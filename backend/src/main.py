from contextlib import asynccontextmanager

from arq import create_pool
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.index import settings
from src.config.redis import redis_settings
from src.db import connect_db, disconnect_db
from src.middlewares.error_middleware import register_error_handlers
from src.repositories.phrase_repository import seed_default_phrases
from src.routes import (
    auth_routes,
    dashboard_log_routes,
    message_routes,
    number_routes,
    phrase_routes,
    session_routes,
    warmup_routes,
)
from src.controllers.auth_controller import ensure_initial_admin
from src.services.auth_service import get_current_user
from src.utils.logger import configure_logging, logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await connect_db()
    await ensure_initial_admin()
    seeded = await seed_default_phrases()
    if seeded:
        logger.info(f"Banco de frases populado com {seeded} frase(s) padrão")
    app.state.redis_pool = await create_pool(redis_settings)
    logger.info(f"{settings.APP_NAME} iniciado ({settings.APP_ENV})")
    yield
    await app.state.redis_pool.close()
    await disconnect_db()
    logger.info(f"{settings.APP_NAME} finalizado")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

protected = [Depends(get_current_user)]
app.include_router(auth_routes.router, prefix=settings.API_PREFIX)
app.include_router(session_routes.router, prefix=settings.API_PREFIX, dependencies=protected)
app.include_router(message_routes.router, prefix=settings.API_PREFIX, dependencies=protected)
app.include_router(warmup_routes.router, prefix=settings.API_PREFIX, dependencies=protected)
app.include_router(phrase_routes.router, prefix=settings.API_PREFIX, dependencies=protected)
app.include_router(number_routes.router, prefix=settings.API_PREFIX, dependencies=protected)
app.include_router(
    dashboard_log_routes.router,
    prefix=settings.API_PREFIX,
    dependencies=protected,
)


@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.APP_ENV}
