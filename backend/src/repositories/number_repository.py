from datetime import datetime

from src.db import db


async def create_number(phone: str, session_name: str, node_id: str):
    return await db.number.create(
        data={
            "phone": phone,
            "sessionName": session_name,
            "nodeId": node_id,
        }
    )


async def get_by_id(number_id: str):
    return await db.number.find_unique(where={"id": number_id}, include={"node": True})


async def get_by_session_name(session_name: str):
    return await db.number.find_unique(where={"sessionName": session_name}, include={"node": True})


async def list_all(active_only: bool = False):
    where = {"active": True} if active_only else {}
    return await db.number.find_many(where=where, include={"node": True}, order={"createdAt": "asc"})


async def update_status(number_id: str, status: str):
    return await db.number.update(where={"id": number_id}, data={"status": status})


async def set_active(number_id: str, active: bool):
    return await db.number.update(where={"id": number_id}, data={"active": active})


async def update_warmup_progress(
    number_id: str,
    warmup_day: int | None = None,
    daily_target: int | None = None,
    daily_sent_count: int | None = None,
    reset_daily: bool = False,
):
    data: dict = {}
    if warmup_day is not None:
        data["warmupDay"] = warmup_day
    if daily_target is not None:
        data["dailyTarget"] = daily_target
    if daily_sent_count is not None:
        data["dailySentCount"] = daily_sent_count
    if reset_daily:
        data["dailySentCount"] = 0
        data["lastResetAt"] = datetime.utcnow()
    if not data:
        return await get_by_id(number_id)
    return await db.number.update(where={"id": number_id}, data=data)


async def increment_daily_sent(number_id: str, amount: int = 1):
    number = await get_by_id(number_id)
    if number is None:
        return None
    return await db.number.update(
        where={"id": number_id},
        data={"dailySentCount": number.dailySentCount + amount},
    )


async def get_or_create_node(name: str, base_url: str, api_key: str | None = None):
    node = await db.wahanode.find_unique(where={"name": name})
    if node:
        return node
    return await db.wahanode.create(
        data={"name": name, "baseUrl": base_url, "apiKey": api_key}
    )
