from pydantic import BaseModel, Field


class WarmupStartRequest(BaseModel):
    number_id: str


class WarmupBulkRequest(BaseModel):
    number_ids: list[str]


class WarmupPairRequest(BaseModel):
    number_a_id: str
    number_b_id: str


class WarmupStatusResponse(BaseModel):
    number_id: str
    phone: str
    active: bool
    warmup_day: int
    daily_target: int
    daily_sent_count: int
    status: str


class WarmupConfigUpdate(BaseModel):
    start_messages: int | None = Field(None, ge=0)
    increment: int | None = Field(None, ge=0)
    max_messages: int | None = Field(None, ge=1)
    max_days: int | None = Field(None, ge=1)
