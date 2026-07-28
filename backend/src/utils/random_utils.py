import random
from datetime import datetime

from src.config.index import settings


def random_delay_seconds(
    min_seconds: int | None = None, max_seconds: int | None = None
) -> int:
    """Delay aleatório entre disparos, para não criar padrão robótico."""
    lo = min_seconds if min_seconds is not None else settings.MESSAGE_MIN_DELAY_SECONDS
    hi = max_seconds if max_seconds is not None else settings.MESSAGE_MAX_DELAY_SECONDS
    if lo > hi:
        lo, hi = hi, lo
    return random.randint(lo, hi)


def is_within_working_hours(now: datetime | None = None) -> bool:
    """Verifica se o horário atual está dentro da janela de funcionamento
    configurada, para não mandar mensagem de madrugada."""
    now = now or datetime.now()
    return settings.WORK_HOUR_START <= now.hour < settings.WORK_HOUR_END


def jitter_ratio(base: float, spread: float = 0.2) -> float:
    """Aplica uma variação percentual aleatória (+/- spread) sobre um valor base."""
    factor = 1 + random.uniform(-spread, spread)
    return max(0.0, base * factor)


def pick_weighted(options: list[tuple[str, float]]) -> str:
    """Escolhe uma opção de uma lista (valor, peso)."""
    values = [o[0] for o in options]
    weights = [o[1] for o in options]
    return random.choices(values, weights=weights, k=1)[0]
