from arq import cron

from src.config.redis import redis_settings
from src.db import connect_db, disconnect_db
from src.jobs.message_job import send_message_job
from src.jobs.warmup_job import run_warmup_cycle
from src.utils.logger import configure_logging, logger


async def startup(ctx):
    configure_logging()
    await connect_db()
    logger.info("Worker arq iniciado")


async def shutdown(ctx):
    await disconnect_db()
    logger.info("Worker arq finalizado")


class WorkerSettings:
    functions = [send_message_job, run_warmup_cycle]
    # Roda a cada minuto; SCHEDULER_INTERVAL_SECONDS < 60 não é suportado pelo
    # cron do arq (granularidade mínima de 1 min) — ajuste a lógica interna
    # do ciclo se precisar de granularidade menor.
    cron_jobs = [
        cron(run_warmup_cycle, second=0),
    ]
    on_startup = startup
    on_shutdown = shutdown
    redis_settings = redis_settings
    max_jobs = 20
