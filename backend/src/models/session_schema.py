from datetime import datetime

from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    phone: str = Field(..., description="Número no formato internacional, ex: 5511999999999")
    node_name: str = Field(..., description="Nome do nó WAHA onde a sessão será criada (ex: kvm8-1)")


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
