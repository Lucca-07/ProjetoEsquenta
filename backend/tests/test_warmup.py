from src.services.warmup_service import calculate_daily_target
from src.config.index import settings


def test_daily_target_starts_at_start_messages():
    assert calculate_daily_target(0) == settings.WARMUP_START_MESSAGES


def test_daily_target_increases_with_day():
    day5 = calculate_daily_target(5)
    day1 = calculate_daily_target(1)
    assert day5 > day1


def test_daily_target_is_capped_at_max_messages():
    far_future_day = settings.WARMUP_MAX_DAYS * 10
    assert calculate_daily_target(far_future_day) == settings.WARMUP_MAX_MESSAGES
