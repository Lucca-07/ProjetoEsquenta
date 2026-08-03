from datetime import datetime, timezone

from src.db import db


async def create_group(
    name: str,
    number_ids: list[str],
    interval_seconds: int,
    duration_hours: int,
    started_at: datetime,
    finish_at: datetime,
):
    group = await db.warmupgroup.create(
        data={
            "name": name.strip(),
            "intervalSeconds": interval_seconds,
            "durationHours": duration_hours,
            "startedAt": started_at,
            "finishAt": finish_at,
        }
    )
    await db.warmupgroupmember.create_many(
        data=[
            {"groupId": group.id, "numberId": number_id}
            for number_id in number_ids
        ]
    )
    return await get_by_id(group.id)


async def get_by_id(group_id: str):
    return await db.warmupgroup.find_unique(
        where={"id": group_id},
        include={
            "members": {
                "include": {
                    "number": {"include": {"node": True}},
                }
            }
        },
    )


async def get_active_for_number(number_id: str):
    return await db.warmupgroup.find_first(
        where={
            "status": "ACTIVE",
            "finishAt": {"gt": datetime.now(timezone.utc)},
            "members": {"some": {"numberId": number_id}},
        },
        include={
            "members": {
                "include": {
                    "number": {"include": {"node": True}},
                }
            }
        },
    )


async def list_active():
    return await db.warmupgroup.find_many(
        where={
            "status": "ACTIVE",
            "finishAt": {"gt": datetime.now(timezone.utc)},
        },
        include={"members": True},
        order={"createdAt": "desc"},
    )


async def set_status(group_id: str, status: str):
    return await db.warmupgroup.update(
        where={"id": group_id},
        data={"status": status},
    )


async def delete_group(group_id: str):
    group = await get_by_id(group_id)
    if group is None:
        return None

    member_ids = [member.numberId for member in group.members]
    active_member_ids = []
    for number_id in member_ids:
        active_group = await get_active_for_number(number_id)
        if active_group and active_group.id == group_id:
            active_member_ids.append(number_id)

    async with db.tx() as transaction:
        await transaction.message.update_many(
            where={
                "groupId": group_id,
                "status": "PENDING",
            },
            data={
                "status": "FAILED",
                "error": "Envio cancelado pela exclusão do esquenta",
            },
        )
        if active_member_ids:
            await transaction.number.update_many(
                where={"id": {"in": active_member_ids}},
                data={
                    "active": False,
                    "warmupStartedAt": None,
                    "warmupFinishAt": None,
                },
            )
        await transaction.message.update_many(
            where={"groupId": group_id},
            data={"groupId": None},
        )
        await transaction.warmupgroupmember.delete_many(
            where={"groupId": group_id}
        )
        return await transaction.warmupgroup.delete(
            where={"id": group_id}
        )
