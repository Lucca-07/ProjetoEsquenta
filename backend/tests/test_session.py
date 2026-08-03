import pytest
from unittest.mock import AsyncMock, MagicMock

from src.services.waha_service import WahaError, WahaService, phone_to_chat_id
from src.models.session_schema import SessionCreate


def test_phone_to_chat_id_strips_non_digits():
    assert phone_to_chat_id("+55 (11) 99999-9999") == "5511999999999@c.us"


def test_session_create_schema_requires_fields():
    payload = SessionCreate(phone="5511999999999", node_name="kvm8-1")
    assert payload.phone == "5511999999999"
    assert payload.node_name == "kvm8-1"


def test_session_create_schema_missing_field_raises():
    with pytest.raises(Exception):
        SessionCreate(phone="5511999999999")


def test_waha_error_preserves_http_status_code():
    error = WahaError("session already exists", status_code=422)

    assert error.status_code == 422


async def test_restart_existing_session_uses_restart_endpoint():
    service = WahaService("http://waha")
    response = MagicMock()
    response.json.return_value = {"name": "session-test"}
    service._request = AsyncMock(return_value=response)

    try:
        await service.restart_existing_session("session-test")
    finally:
        await service.close()

    assert service._request.await_count == 1
    assert service._request.await_args_list[0].args[:2] == (
        "POST",
        "/api/sessions/session-test/restart",
    )
