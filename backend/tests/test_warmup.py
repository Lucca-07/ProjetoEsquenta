import inspect
from types import SimpleNamespace

from src.controllers.warmup_controller import start_warmup
from src.services.warmup_service import calculate_daily_target
from src.config.index import settings
from src.controllers.number_controller import _remaining_label, _status_label


def test_daily_target_starts_at_start_messages():
    assert calculate_daily_target(0) == settings.WARMUP_START_MESSAGES


def test_daily_target_increases_with_day():
    day5 = calculate_daily_target(5)
    day1 = calculate_daily_target(1)
    assert day5 > day1


def test_daily_target_is_capped_at_max_messages():
    far_future_day = settings.WARMUP_MAX_DAYS * 10
    assert calculate_daily_target(far_future_day) == settings.WARMUP_MAX_MESSAGES


def test_number_without_active_warmup_has_zero_remaining_time():
    number = SimpleNamespace(warmupFinishAt=None)

    assert _remaining_label(number) == "0min"


def test_number_without_active_warmup_has_no_action_status():
    number = SimpleNamespace(
        status="WORKING",
        active=False,
        warmupStartedAt=None,
        warmupFinishAt=None,
    )

    assert _status_label(number) == "Sem ação"


def test_stopped_session_has_disconnected_status():
    number = SimpleNamespace(
        status="STOPPED",
        active=False,
        warmupStartedAt=None,
        warmupFinishAt=None,
    )

    assert _status_label(number) == "Desconectado"


def test_individual_warmup_start_has_default_configuration():
    parameters = inspect.signature(start_warmup).parameters

    assert parameters["interval_seconds"].default == 240
    assert parameters["duration_hours"].default == 24
