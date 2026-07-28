from src.db import connect_db
from src.services.scheduler_service import run_scheduling_cycle
from src.utils.logger import logger


async def run_warmup_cycle(ctx):
    """Tarefa cron: roda a cada SCHEDULER_INTERVAL_SECONDS (ver WorkerSettings)
    e agenda os envios pendentes de todos os números ativos."""
    await connect_db()
    redis_pool = ctx["redis"]
    count = await run_scheduling_cycle(redis_pool)
    if count:
        logger.info(f"[warmup_job] {count} mensagem(ns) agendada(s) neste ciclo")
