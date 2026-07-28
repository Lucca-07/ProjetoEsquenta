from fastapi import HTTPException, Request

from src.repositories import number_repository, warmup_log_repository, phrase_repository
from src.utils.spintax import random_warmup_message


async def send_message(request: Request, sender_id: str, receiver_id: str, content: str | None):
    sender = await number_repository.get_by_id(sender_id)
    receiver = await number_repository.get_by_id(receiver_id)
    if sender is None or receiver is None:
        raise HTTPException(status_code=404, detail="Remetente ou destinatário não encontrado")

    text = content
    if not text:
        active_phrases = await phrase_repository.list_phrases(active_only=True)
        templates = [p.text for p in active_phrases] if active_phrases else None
        text = random_warmup_message(templates)
    message = await warmup_log_repository.create_message(sender_id, receiver_id, text)

    redis_pool = request.app.state.redis_pool
    await redis_pool.enqueue_job("send_message_job", message.id, sender.warmupDay)
    return message


async def get_history(number_id: str, limit: int = 50):
    number = await number_repository.get_by_id(number_id)
    if number is None:
        raise HTTPException(status_code=404, detail="Número não encontrado")
    return await warmup_log_repository.list_messages_for_number(number_id, limit)
