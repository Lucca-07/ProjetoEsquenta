from datetime import datetime, timezone

from src.config.index import settings
from src.repositories import number_repository, warmup_log_repository, phrase_repository
from src.services import pairing_service
from src.utils.logger import logger
from src.utils.random_utils import is_within_working_hours
from src.utils.spintax import random_warmup_message


def calculate_daily_target(warmup_day: int) -> int:
    """Curva de rampa: começa em WARMUP_START_MESSAGES e cresce
    WARMUP_INCREMENT por dia, até o teto WARMUP_MAX_MESSAGES."""
    target = settings.WARMUP_START_MESSAGES + settings.WARMUP_INCREMENT * warmup_day
    return min(target, settings.WARMUP_MAX_MESSAGES)


def _is_new_day(last_reset_at: datetime) -> bool:
    now = datetime.now(timezone.utc)
    if last_reset_at.tzinfo is None:
        last_reset_at = last_reset_at.replace(tzinfo=timezone.utc)
    return now.date() > last_reset_at.date()


async def advance_day_if_needed(number) -> object:
    """Se já virou o dia desde o último reset, avança warmup_day (até o
    máximo configurado), zera o contador diário e recalcula a meta."""
    if not _is_new_day(number.lastResetAt):
        return number

    next_day = min(number.warmupDay + 1, settings.WARMUP_MAX_DAYS)
    new_target = calculate_daily_target(next_day)

    updated = await number_repository.update_warmup_progress(
        number.id, warmup_day=next_day, daily_target=new_target, reset_daily=True
    )
    await warmup_log_repository.add_log(
        number.id, day=next_day, event="DAY_ADVANCED",
        detail=f"Nova meta diária: {new_target} mensagens",
    )
    logger.info(f"[warmup] {number.phone} avançou para o dia {next_day} (meta={new_target})")
    return updated


async def is_number_due_for_message(number) -> bool:
    if not number.active or number.status != "WORKING":
        return False
    if not is_within_working_hours():
        return False
    return number.dailySentCount < number.dailyTarget


async def prepare_next_message(number):
    """Escolhe um parceiro e cria o registro de Message (status PENDING)
    pronto para ser enviado por um job. Retorna None se não houver parceiro
    disponível."""
    partner = await pairing_service.get_partner_for(number)
    if partner is None:
        return None

    await pairing_service.ensure_pair(number.id, partner.id)

    active_phrases = await phrase_repository.list_phrases(active_only=True)
    templates = [p.text for p in active_phrases] if active_phrases else None
    content = random_warmup_message(templates)

    message = await warmup_log_repository.create_message(
        sender_id=number.id, receiver_id=partner.id, content=content
    )
    return message


async def register_send_result(number_id: str, day: int, success: bool, detail: str | None = None):
    if success:
        await number_repository.increment_daily_sent(number_id)
    await warmup_log_repository.add_log(
        number_id,
        day=day,
        event="MESSAGE_SENT" if success else "SEND_ERROR",
        detail=detail,
        messages_sent=1 if success else 0,
    )
