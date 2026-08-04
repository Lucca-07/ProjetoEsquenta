from unittest.mock import AsyncMock, MagicMock

import pytest

from src.models.session_schema import SessionCreate
from src.services.evolution_service import (
    EvolutionError,
    EvolutionService,
    normalize_evolution_status,
    normalize_phone,
)


def test_normalize_phone_strips_non_digits():
    assert normalize_phone("+55 (11) 99999-9999") == "5511999999999"


def test_session_create_schema_requires_fields():
    payload = SessionCreate(phone="5511999999999", node_name="kvm8-1")
    assert payload.phone == "5511999999999"
    assert payload.node_name == "kvm8-1"


def test_session_create_schema_missing_field_raises():
    with pytest.raises(Exception):
        SessionCreate(phone="5511999999999")


def test_evolution_error_preserves_http_status_code():
    error = EvolutionError("instance already exists", status_code=403)
    assert error.status_code == 403


@pytest.mark.parametrize(
    ("state", "expected"),
    [
        ("open", "WORKING"),
        ("connecting", "SCAN_QR_CODE"),
        ("close", "STOPPED"),
        (None, "STARTING"),
    ],
)
def test_normalizes_evolution_state(state, expected):
    assert normalize_evolution_status(state) == expected


async def test_restart_instance_uses_evolution_endpoint():
    service = EvolutionService("http://evolution")
    response = MagicMock(content=b"{}")
    response.json.return_value = {"instance": {"instanceName": "session-test"}}
    service._request = AsyncMock(return_value=response)

    try:
        await service.restart_instance("session-test")
    finally:
        await service.close()

    assert service._request.await_args_list[0].args[:2] == (
        "PUT",
        "/instance/restart/session-test",
    )


async def test_send_text_uses_number_without_chat_suffix():
    service = EvolutionService("http://evolution", "secret")
    response = MagicMock()
    response.json.return_value = {"key": {"id": "ABC123"}}
    service._request = AsyncMock(return_value=response)

    try:
        await service.send_text_message(
            "session-test", "+55 (11) 99999-9999", "Oi"
        )
    finally:
        await service.close()

    call = service._request.await_args_list[0]
    assert call.args[:2] == ("POST", "/message/sendText/session-test")
    assert call.kwargs["json"] == {"number": "5511999999999", "text": "Oi"}
