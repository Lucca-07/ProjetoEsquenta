from datetime import datetime, timezone

from src.db import connect_db
from src.repositories import warmup_log_repository, number_repository
from src.services import warmup_service
from src.services.waha_service import (
    WahaError,
    build_waha_service_for_node,
    extract_message_id,
    phone_to_chat_id,
)
from src.utils.logger import logger


def _warmup_is_active(number) -> bool:
    return (
        number.active
        and number.warmupStartedAt is not None
        and number.warmupFinishAt is not None
        and datetime.now(timezone.utc) < number.warmupFinishAt
    )


async def send_message_job(ctx, message_id: str, warmup_day: int):
    """Envia uma mensagem PENDING via WAHA, usando o nó (servidor) correto
    do número remetente, e atualiza status/log."""
    await connect_db()

    message = await warmup_log_repository.get_message(message_id)
    if message is None:
        logger.error(f"[message_job] mensagem {message_id} não encontrada")
        return
    if message.status != "PENDING":
        logger.info(
            f"[message_job] mensagem {message_id} ignorada: status={message.status}"
        )
        return

    sender = await number_repository.get_by_id(message.senderId)
    receiver = await number_repository.get_by_id(message.receiverId)
    if sender is None or receiver is None:
        await warmup_log_repository.mark_message_failed(message_id, "sender/receiver não encontrado")
        return

    if not _warmup_is_active(sender):
        await warmup_log_repository.mark_message_failed(
            message_id,
            "Aquecimento parado antes do envio",
        )
        logger.info(
            f"[message_job] envio {message_id} cancelado: aquecimento inativo"
        )
        return

    waha = await build_waha_service_for_node(sender.node)
    try:
        chat_id = phone_to_chat_id(receiver.phone)
        result = await waha.send_text_message(sender.sessionName, chat_id, message.content)
        wa_message_id = extract_message_id(result)
        await warmup_log_repository.mark_message_sent(message_id, wa_message_id)
        await warmup_service.register_send_result(sender.id, warmup_day, success=True)
        logger.info(f"[message_job] {sender.phone} -> {receiver.phone} enviado (day={warmup_day})")
    except WahaError as exc:
        await warmup_log_repository.mark_message_failed(message_id, str(exc))
        await warmup_service.register_send_result(sender.id, warmup_day, success=False, detail=str(exc))
        logger.error(f"[message_job] falha ao enviar {sender.phone} -> {receiver.phone}: {exc}")
    finally:
        await waha.close()
