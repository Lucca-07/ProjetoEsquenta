import base64
import binascii
import hashlib
import hmac
import json
import os
import time

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config.index import settings
from src.repositories import user_repository


bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    iterations = 600_000
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt,
        iterations,
    )
    return (
        f"pbkdf2_sha256${iterations}$"
        f"{base64.urlsafe_b64encode(salt).decode()}$"
        f"{base64.urlsafe_b64encode(digest).decode()}"
    )


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            base64.urlsafe_b64decode(salt),
            int(iterations),
        )
        return hmac.compare_digest(
            actual,
            base64.urlsafe_b64decode(expected),
        )
    except (ValueError, TypeError, binascii.Error):
        return False


def _encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _decode(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def create_access_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": int(time.time()) + settings.AUTH_TOKEN_HOURS * 3600,
    }
    encoded_payload = _encode(
        json.dumps(payload, separators=(",", ":")).encode()
    )
    signature = hmac.new(
        settings.AUTH_SECRET.encode(),
        encoded_payload.encode(),
        hashlib.sha256,
    ).digest()
    return f"{encoded_payload}.{_encode(signature)}"


def decode_access_token(token: str) -> dict:
    try:
        encoded_payload, encoded_signature = token.split(".", 1)
        expected = hmac.new(
            settings.AUTH_SECRET.encode(),
            encoded_payload.encode(),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(expected, _decode(encoded_signature)):
            raise ValueError
        payload = json.loads(_decode(encoded_payload))
        if not isinstance(payload.get("sub"), str):
            raise ValueError
        if payload.get("exp", 0) < time.time():
            raise ValueError
        return payload
    except (ValueError, TypeError, binascii.Error, UnicodeDecodeError):
        raise HTTPException(
            status_code=401,
            detail="Sessão inválida ou expirada",
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Autenticação necessária")
    payload = decode_access_token(credentials.credentials)
    user = await user_repository.get_by_id(payload["sub"])
    if user is None or not user.active:
        raise HTTPException(
            status_code=401,
            detail="Usuário inativo ou inexistente",
        )
    return user


async def require_admin(user=Depends(get_current_user)):
    if user.role != "ADMIN":
        raise HTTPException(
            status_code=403,
            detail="Acesso exclusivo para administradores",
        )
    return user
