from datetime import datetime

from pydantic import BaseModel, Field


class MessageSendRequest(BaseModel):
    sender_id: str = Field(..., description="ID do número remetente")
    receiver_id: str = Field(..., description="ID do número destinatário")
    content: str | None = Field(
        None, description="Texto da mensagem; se omitido, um texto de aquecimento é gerado automaticamente"
    )


class MessageResponse(BaseModel):
    id: str
    sender_id: str
    receiver_id: str
    content: str
    status: str
    wa_message_id: str | None
    error: str | None
    created_at: datetime
    sent_at: datetime | None

    class Config:
        from_attributes = True
