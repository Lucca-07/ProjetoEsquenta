from datetime import datetime

from pydantic import BaseModel, Field


class PhraseCreate(BaseModel):
    text: str = Field(..., min_length=1, description="Texto em spintax, ex: '{Oi|Olá}, tudo bem?'")
    category: str = Field("geral", description="saudacao, despedida, confirmacao, geral...")


class PhraseUpdate(BaseModel):
    text: str | None = None
    category: str | None = None
    active: bool | None = None


class PhraseResponse(BaseModel):
    id: str
    text: str
    category: str
    active: bool
    created_at: datetime

    class Config:
        from_attributes = True
