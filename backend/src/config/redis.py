from urllib.parse import urlparse

from arq.connections import RedisSettings

from src.config.index import settings


def get_redis_url() -> str:
    return settings.REDIS_URL


def _build_redis_settings() -> RedisSettings:
    parsed = urlparse(settings.REDIS_URL)
    db = 0
    if parsed.path and parsed.path.strip("/"):
        db = int(parsed.path.strip("/"))
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        password=parsed.password,
        database=db,
    )


redis_settings = _build_redis_settings()
