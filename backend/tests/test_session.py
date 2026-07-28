import pytest

from src.services.waha_service import phone_to_chat_id
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
