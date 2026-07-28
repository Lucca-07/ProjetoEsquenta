from arq import ArqRedis

from src.repositories import number_repository
from src.services import warmup_service
from src.utils.logger import logger
from src.utils.random_utils import random_delay_seconds


async def run_scheduling_cycle(redis_pool: ArqRedis) -> int:
    """Executado periodicamente pelo cron do worker arq (ver jobs/warmup_job.py).
    Para cada número ativo: avança o dia se necessário e, se ainda não bateu
    a meta diária, prepara a próxima mensagem e agenda o envio com um atraso
    aleatório (para não enviar tudo de uma vez / evitar padrão robótico)."""

    numbers = await number_repository.list_all(active_only=True)
    scheduled = 0

    for number in numbers:
        number = await warmup_service.advance_day_if_needed(number)

        if not await warmup_service.is_number_due_for_message(number):
            continue

        message = await warmup_service.prepare_next_message(number)
        if message is None:
            logger.warning(f"[scheduler] {number.phone} sem parceiro disponível, pulando")
            continue

        delay = random_delay_seconds()
        await redis_pool.enqueue_job("send_message_job", message.id, number.warmupDay, _defer_by=delay)
        scheduled += 1
        logger.debug(f"[scheduler] mensagem {message.id} agendada em {delay}s para {number.phone}")

    return scheduled
