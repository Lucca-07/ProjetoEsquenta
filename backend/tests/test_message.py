from src.utils.spintax import parse_spintax, random_warmup_message
from src.utils.random_utils import random_delay_seconds, is_within_working_hours
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from src.jobs.message_job import _warmup_is_active
from src.services.waha_service import extract_message_id, phone_to_chat_id


def test_spintax_resolves_single_option():
    assert parse_spintax("{Olá}") == "Olá"


def test_spintax_picks_one_of_the_options():
    result = parse_spintax("{a|b|c}")
    assert result in {"a", "b", "c"}


def test_spintax_handles_text_without_braces():
    assert parse_spintax("mensagem simples") == "mensagem simples"


def test_random_warmup_message_is_non_empty_and_has_no_braces():
    msg = random_warmup_message()
    assert msg
    assert "{" not in msg and "}" not in msg


def test_random_delay_within_bounds():
    delay = random_delay_seconds(10, 20)
    assert 10 <= delay <= 20


def test_working_hours_check():
    inside = datetime(2026, 1, 1, 12, 0)
    outside = datetime(2026, 1, 1, 3, 0)
    assert is_within_working_hours(inside) is True
    assert is_within_working_hours(outside) is False


def test_stopped_warmup_is_not_active_for_queued_message():
    number = SimpleNamespace(
        active=False,
        warmupStartedAt=None,
        warmupFinishAt=None,
    )

    assert _warmup_is_active(number) is False


def test_running_warmup_is_active_for_queued_message():
    now = datetime.now(timezone.utc)
    number = SimpleNamespace(
        active=True,
        warmupStartedAt=now - timedelta(minutes=1),
        warmupFinishAt=now + timedelta(hours=1),
    )

    assert _warmup_is_active(number) is True


def test_extracts_serialized_id_from_waha_object():
    result = {
        "id": {
            "fromMe": True,
            "id": "ABC123",
            "_serialized": "true_5511999999999@c.us_ABC123",
        }
    }

    assert (
        extract_message_id(result)
        == "true_5511999999999@c.us_ABC123"
    )


def test_keeps_string_message_id():
    assert extract_message_id({"id": "message-id"}) == "message-id"


def test_adds_brazil_country_code_to_local_phone():
    assert phone_to_chat_id("11 95360-8050") == "5511953608050@c.us"


def test_preserves_phone_that_already_has_country_code():
    assert phone_to_chat_id("55 11 95360-8050") == "5511953608050@c.us"
