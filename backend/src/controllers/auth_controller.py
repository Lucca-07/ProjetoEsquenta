from fastapi import HTTPException

from src.config.index import settings
from src.models.auth_schema import LoginRequest, UserCreateRequest
from src.repositories import user_repository
from src.services.auth_service import (
    create_access_token,
    hash_password,
    verify_password,
)
from src.utils.logger import logger


def serialize_user(user) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "active": user.active,
    }


async def login(payload: LoginRequest):
    user = await user_repository.get_by_email(payload.email)
    if (
        user is None
        or not user.active
        or not verify_password(payload.password, user.passwordHash)
    ):
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
        "user": serialize_user(user),
    }


async def create_user(payload: UserCreateRequest):
    if await user_repository.get_by_email(payload.email):
        raise HTTPException(status_code=409, detail="Este email já está cadastrado")
    user = await user_repository.create_user(
        payload.name,
        payload.email,
        hash_password(payload.password),
        payload.role,
    )
    return serialize_user(user)


async def list_users():
    users = await user_repository.list_all()
    return [serialize_user(user) for user in users]


async def ensure_initial_admin():
    existing = await user_repository.get_by_email(settings.ADMIN_EMAIL)
    if existing:
        return False
    await user_repository.create_user(
        settings.ADMIN_NAME,
        settings.ADMIN_EMAIL,
        hash_password(settings.ADMIN_PASSWORD),
        "ADMIN",
    )
    logger.info(f"Administrador inicial criado: {settings.ADMIN_EMAIL}")
    return True
