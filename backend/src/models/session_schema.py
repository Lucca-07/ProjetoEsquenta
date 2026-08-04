from datetime import datetime

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    phone: str = Field(..., description="Número no formato internacional, ex: 5511999999999")
    node_name: str = Field(..., description="Nome do no Evolution onde a instancia sera criada (ex: kvm8-1)")


class SessionResponse(BaseModel):
    id: str
    phone: str
    session_name: str
    node_name: str
    status: str
    active: bool
    warmup_day: int
    daily_target: int
    daily_sent_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class SessionStatusResponse(BaseModel):
    session_name: str
    status: str
    qr: str | None = None
    number_id: str | None = None


class PendingSessionResponse(BaseModel):
    session_name: str
    phone: str
    node_name: str
    status: str


class PairingCodeRequest(BaseModel):
    phone: str
    node_name: str
