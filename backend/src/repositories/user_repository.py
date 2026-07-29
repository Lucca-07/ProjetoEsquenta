from src.db import db


async def get_by_id(user_id: str):
    return await db.user.find_unique(where={"id": user_id})


async def get_by_email(email: str):
    return await db.user.find_unique(where={"email": email.lower().strip()})


async def list_all():
    return await db.user.find_many(order={"createdAt": "desc"})


async def create_user(
    name: str,
    email: str,
    password_hash: str,
    role: str,
):
    return await db.user.create(
        data={
            "name": name.strip(),
            "email": email.lower().strip(),
            "passwordHash": password_hash,
            "role": role,
        }
    )
