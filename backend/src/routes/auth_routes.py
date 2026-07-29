from fastapi import APIRouter, Depends

from src.controllers import auth_controller
from src.models.auth_schema import (
    LoginRequest,
    LoginResponse,
    UserCreateRequest,
    UserResponse,
)
from src.services.auth_service import get_current_user, require_admin


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
async def login(payload: LoginRequest):
    return await auth_controller.login(payload)


@router.get("/me", response_model=UserResponse)
async def me(user=Depends(get_current_user)):
    return auth_controller.serialize_user(user)


@router.get(
    "/users",
    response_model=list[UserResponse],
    dependencies=[Depends(require_admin)],
)
async def list_users():
    return await auth_controller.list_users()


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=201,
    dependencies=[Depends(require_admin)],
)
async def create_user(payload: UserCreateRequest):
    return await auth_controller.create_user(payload)
