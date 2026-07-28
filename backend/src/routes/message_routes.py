from fastapi import APIRouter, Request

from src.controllers import message_controller
from src.models.message_schema import MessageSendRequest

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", status_code=202)
async def send_message(payload: MessageSendRequest, request: Request):
    return await message_controller.send_message(
        request, payload.sender_id, payload.receiver_id, payload.content
    )


@router.get("/{number_id}/history")
async def get_history(number_id: str, limit: int = 50):
    return await message_controller.get_history(number_id, limit)
