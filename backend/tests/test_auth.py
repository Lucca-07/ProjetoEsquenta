import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from src.models.auth_schema import UserCreateRequest
from src.services.auth_service import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verification():
    encoded = hash_password("SenhaSegura@123")

    assert encoded != "SenhaSegura@123"
    assert verify_password("SenhaSegura@123", encoded)
    assert not verify_password("senha-incorreta", encoded)


def test_access_token_round_trip():
    token = create_access_token("user-id")

    assert decode_access_token(token)["sub"] == "user-id"


def test_rejects_invalid_access_token():
    with pytest.raises(HTTPException) as error:
        decode_access_token("token-invalido")

    assert error.value.status_code == 401


def test_normalizes_email_and_accepts_roles():
    payload = UserCreateRequest(
        name="Maria",
        email="  MARIA@EXEMPLO.COM  ",
        password="SenhaSegura@123",
        role="ADMIN",
    )

    assert payload.email == "maria@exemplo.com"
    assert payload.role == "ADMIN"


def test_rejects_invalid_role():
    with pytest.raises(ValidationError):
        UserCreateRequest(
            name="Maria",
            email="maria@exemplo.com",
            password="SenhaSegura@123",
            role="GESTOR",
        )
