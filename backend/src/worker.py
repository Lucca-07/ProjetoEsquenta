import asyncio

from src.config.index import settings
from src.config.redis import redis_settings
from src.db import connect_db, disconnect_db
from src.jobs.message_job import send_message_job
from src.jobs.warmup_job import run_warmup_cycle
from src.utils.logger import configure_logging, logger


async def scheduler_loop(ctx):
    interval = max(5, min(settings.SCHEDULER_INTERVAL_SECONDS, 10))
    while True:
        try:
            await run_warmup_cycle(ctx)
        except Exception:
            logger.exception("Falha no ciclo do scheduler")
        await asyncio.sleep(interval)


async def startup(ctx):
    configure_logging()
    await connect_db()
    ctx["scheduler_task"] = asyncio.create_task(scheduler_loop(ctx))
    logger.info("Worker arq iniciado")


async def shutdown(ctx):
    task = ctx.get("scheduler_task")
    if task:
        task.cancel()
    await disconnect_db()
    logger.info("Worker arq finalizado")


class WorkerSettings:
    functions = [send_message_job, run_warmup_cycle]
    cron_jobs = []
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = redis_settings
    max_jobs = 20
