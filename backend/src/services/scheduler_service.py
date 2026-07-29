from datetime import datetime, timezone

from arq import ArqRedis

from src.repositories import number_repository
from src.services import warmup_service
from src.utils.logger import logger
from src.utils.random_utils import random_delay_seconds


async def run_scheduling_cycle(redis_pool: ArqRedis) -> int:
    numbers = await number_repository.list_all(active_only=True)
    scheduled = 0

    for number in numbers:
        # Encerra automaticamente quando a duração acabar
        if (
            number.warmupFinishAt is not None
            and datetime.now(timezone.utc) >= number.warmupFinishAt
        ):
            await number_repository.set_active(number.id, False)

            logger.info(f"[scheduler] Aquecimento encerrado para {number.phone}")

            continue

        number = await warmup_service.advance_day_if_needed(number)

        if not await warmup_service.is_number_due_for_message(number):
            continue

        message = await warmup_service.prepare_next_message(number)

        if message is None:
            logger.warning(
                f"[scheduler] {number.phone} sem parceiro disponível, pulando"
            )
            continue

        variacao = max(5, int(number.intervalSeconds * 0.1))

        delay = random_delay_seconds(
            min_seconds=max(1, number.intervalSeconds - variacao),
            max_seconds=number.intervalSeconds + variacao,
        )

        await redis_pool.enqueue_job(
            "send_message_job",
            message.id,
            number.warmupDay,
            _defer_by=delay,
        )

        scheduled += 1

        logger.debug(
            f"[scheduler] mensagem {message.id} agendada em {delay}s para {number.phone}"
        )

    return scheduled
