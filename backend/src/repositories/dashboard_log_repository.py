from src.db import db


async def get_numbers():
    return await db.number.find_many(order={"phone": "asc"})


async def get_messages():
    return await db.message.find_many(order={"createdAt": "desc"})


async def get_groups():
    return await db.warmupgroup.find_many(
        include={
            "members": {
                "include": {
                    "number": True,
                }
            }
        },
        order={"startedAt": "desc"},
    )
