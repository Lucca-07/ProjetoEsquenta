from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models.session_schema import SessionCreate
from src.services.evolution_go_service import (
    EvolutionGoError,
    EvolutionGoService,
    evolution_go_instance_id,
    evolution_go_instance_token,
    normalize_evolution_status,
    normalize_phone,
)


def test_normalize_phone_strips_non_digits():
    assert normalize_phone("+55 (11) 99999-9999") == "5511999999999"


def test_session_schema_supports_both_connection_methods():
    default = SessionCreate(phone="5511999999999", node_name="kvm8-1")
    code = SessionCreate(
        phone="5511999999999", node_name="kvm8-1", connection_method="code"
    )
    assert default.connection_method == "qr"
    assert code.connection_method == "code"


def test_session_create_schema_missing_field_raises():
    with pytest.raises(Exception):
        SessionCreate(phone="5511999999999")


def test_evolution_go_error_preserves_http_status_code():
    error = EvolutionGoError("instance already exists", status_code=500)
    assert error.status_code == 500


def test_instance_credentials_are_stable_and_distinct():
    assert evolution_go_instance_id("session-test") == evolution_go_instance_id(
        "session-test"
    )
    assert evolution_go_instance_token("secret", "one") != evolution_go_instance_token(
        "secret", "two"
    )


@pytest.mark.parametrize(
    ("connected", "logged_in", "expected"),
    [
        (True, True, "WORKING"),
        (True, False, "SCAN_QR_CODE"),
        (False, False, "STOPPED"),
    ],
)
def test_normalizes_evolution_go_state(connected, logged_in, expected):
    assert normalize_evolution_status(connected, logged_in) == expected


async def test_create_instance_uses_admin_key_and_instance_token():
    service = EvolutionGoService("http://evolution-go", "secret")
    response = MagicMock()
    response.json.return_value = {"message": "success"}
    service._request = AsyncMock(return_value=response)
    try:
        await service.create_instance("session-test")
    finally:
        await service.close()

    call = service._request.await_args_list[0]
    assert call.args[:2] == ("POST", "/instance/create")
    assert call.kwargs["json"]["token"] == evolution_go_instance_token(
        "secret", "session-test"
    )


async def test_pairing_code_uses_instance_endpoint_and_token():
    service = EvolutionGoService("http://evolution-go", "secret")
    response = MagicMock()
    response.json.return_value = {"data": {"PairingCode": "ABC12345"}}
    service._request = AsyncMock(return_value=response)
    try:
        code = await service.request_pairing_code(
            "session-test", "+55 (11) 99999-9999"
        )
    finally:
        await service.close()

    call = service._request.await_args_list[0]
    assert code == "ABC12345"
    assert call.args[:2] == ("POST", "/instance/pair")
    assert call.kwargs["json"] == {"phone": "5511999999999"}
    assert call.kwargs["headers"]["apikey"] != "secret"


async def test_send_text_uses_evolution_go_endpoint():
    service = EvolutionGoService("http://evolution-go", "secret")
    response = MagicMock()
    response.json.return_value = {"data": {"Info": {"ID": "ABC123"}}}
    service._request = AsyncMock(return_value=response)
    try:
        await service.send_text_message(
            "session-test", "+55 (11) 99999-9999", "Oi"
        )
    finally:
        await service.close()

    call = service._request.await_args_list[0]
    assert call.args[:2] == ("POST", "/send/text")
    assert call.kwargs["json"] == {"number": "5511999999999", "text": "Oi"}
