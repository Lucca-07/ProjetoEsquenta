from src.db import db


async def add_log(number_id: str, day: int, event: str, detail: str | None = None,
                   messages_sent: int = 0, messages_received: int = 0):
    return await db.warmuplog.create(
        data={
            "numberId": number_id,
            "day": day,
            "event": event,
            "detail": detail,
            "messagesSent": messages_sent,
            "messagesReceived": messages_received,
        }
    )


async def get_logs_for_number(number_id: str, limit: int = 50):
    return await db.warmuplog.find_many(
        where={"numberId": number_id},
        order={"createdAt": "desc"},
        take=limit,
    )


async def create_message(sender_id: str, receiver_id: str, content: str):
    return await db.message.create(
        data={
            "senderId": sender_id,
            "receiverId": receiver_id,
            "content": content,
            "status": "PENDING",
        }
    )


async def mark_message_sent(message_id: str, wa_message_id: str | None):
    from datetime import datetime

    return await db.message.update(
        where={"id": message_id},
        data={"status": "SENT", "waMessageId": wa_message_id, "sentAt": datetime.utcnow()},
    )


async def mark_message_failed(message_id: str, error: str):
    return await db.message.update(
        where={"id": message_id}, data={"status": "FAILED", "error": error}
    )


async def get_message(message_id: str):
    return await db.message.find_unique(where={"id": message_id})


async def list_messages_for_number(number_id: str, limit: int = 50):
    return await db.message.find_many(
        where={"OR": [{"senderId": number_id}, {"receiverId": number_id}]},
        order={"createdAt": "desc"},
        take=limit,
    )


async def get_or_create_pair(number_a_id: str, number_b_id: str):
    existing = await db.warmuppair.find_first(
        where={
            "OR": [
                {"numberAId": number_a_id, "numberBId": number_b_id},
                {"numberAId": number_b_id, "numberBId": number_a_id},
            ]
        }
    )
    if existing:
        return existing
    return await db.warmuppair.create(
        data={"numberAId": number_a_id, "numberBId": number_b_id}
    )


async def list_active_pairs():
    return await db.warmuppair.find_many(
        where={"active": True}, include={"numberA": True, "numberB": True}
    )
