from typing import Literal

from pydantic import BaseModel, Field, field_validator


class EmailModel(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        local, separator, domain = normalized.partition("@")
        if not separator or not local or "." not in domain:
            raise ValueError("Informe um email válido")
        return normalized


class LoginRequest(EmailModel):
    password: str = Field(..., min_length=8, max_length=128)


class UserCreateRequest(EmailModel):
    name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8, max_length=128)
    role: Literal["ADMIN", "USER"] = "USER"


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    active: bool


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
