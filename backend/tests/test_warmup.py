import inspect
from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from src.controllers.warmup_controller import start_warmup
from src.models.warmup_schema import WarmupBulkRequest
from src.services import pairing_service
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


def test_group_warmup_accepts_multiple_numbers():
    request = WarmupBulkRequest(
        name="Grupo principal",
        number_ids=["numero-1", "numero-2", "numero-3"],
        interval_seconds=240,
        duration_hours=24,
    )

    assert len(request.number_ids) == 3


def test_group_warmup_requires_at_least_two_numbers():
    with pytest.raises(ValidationError):
        WarmupBulkRequest(
            name="Grupo principal",
            number_ids=["numero-1"],
            interval_seconds=240,
            duration_hours=24,
        )


@pytest.mark.asyncio
async def test_partner_is_selected_only_from_same_group(monkeypatch):
    sender = SimpleNamespace(id="sender")
    allowed = SimpleNamespace(
        id="allowed",
        active=True,
        status="WORKING",
        warmupStartedAt=object(),
        warmupFinishAt=object(),
    )
    outside = SimpleNamespace(
        id="outside",
        active=True,
        status="WORKING",
        warmupStartedAt=object(),
        warmupFinishAt=object(),
    )
    group = SimpleNamespace(
        members=[
            SimpleNamespace(numberId="sender", number=sender),
            SimpleNamespace(numberId="allowed", number=allowed),
        ]
    )

    async def get_group(_number_id):
        return group

    monkeypatch.setattr(
        pairing_service.warmup_group_repository,
        "get_active_for_number",
        get_group,
    )

    selected = await pairing_service.get_partner_for(sender)

    assert selected is allowed
    assert selected is not outside
