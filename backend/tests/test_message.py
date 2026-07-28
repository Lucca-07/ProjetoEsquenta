from src.utils.spintax import parse_spintax, random_warmup_message
from src.utils.random_utils import random_delay_seconds, is_within_working_hours
from datetime import datetime


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
