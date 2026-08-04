import random


def random_delay_seconds(min_seconds: int, max_seconds: int) -> int:
    """Return a random delay inside the interval configured for a warmup."""
    lo, hi = sorted((min_seconds, max_seconds))
    return random.randint(lo, hi)


def jitter_ratio(base: float, spread: float = 0.2) -> float:
    factor = 1 + random.uniform(-spread, spread)
    return max(0.0, base * factor)


def pick_weighted(options: list[tuple[str, float]]) -> str:
    values = [option[0] for option in options]
    weights = [option[1] for option in options]
    return random.choices(values, weights=weights, k=1)[0]
