from pydantic import BaseModel, Field


class WarmupStartRequest(BaseModel):
    number_id: str


class WarmupBulkRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    number_ids: list[str] = Field(..., min_length=2)

    interval_seconds: int = Field(..., ge=10, le=3600)

    duration_hours: int = Field(..., ge=1, le=720)


class WarmupSelectionRequest(BaseModel):
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
