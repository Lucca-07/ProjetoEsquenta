from collections import defaultdict
from datetime import datetime, timedelta, timezone

from src.repositories import dashboard_log_repository
from src.repositories import warmup_group_repository
from fastapi import HTTPException


async def get_dashboard(
    days: int | None = None,
    phone: str | None = None,
    status: str | None = None,
):
    numbers = await dashboard_log_repository.get_numbers()
    messages = await dashboard_log_repository.get_messages()
    groups = await dashboard_log_repository.get_groups()

    cutoff = (
        datetime.now(timezone.utc) - timedelta(days=days)
        if days
        else None
    )
    phone_term = "".join(character for character in (phone or "") if character.isdigit())
    matching_number_ids = {
        number.id
        for number in numbers
        if not phone_term
        or phone_term in "".join(
            character for character in number.phone if character.isdigit()
        )
    }
    messages = [
        message
        for message in messages
        if (not cutoff or message.createdAt.replace(tzinfo=timezone.utc) >= cutoff)
        and (
            not phone_term
            or message.senderId in matching_number_ids
            or message.receiverId in matching_number_ids
        )
    ]
    groups = [
        group
        for group in groups
        if (not cutoff or group.startedAt.replace(tzinfo=timezone.utc) >= cutoff)
        and (not status or group.status == status)
        and (
            not phone_term
            or any(
                member.numberId in matching_number_ids
                for member in group.members
            )
        )
    ]
    if status:
        visible_group_ids = {group.id for group in groups}
        messages = [
            message
            for message in messages
            if message.groupId in visible_group_ids
        ]
    visible_numbers = [
        number
        for number in numbers
        if not phone_term or number.id in matching_number_ids
    ]

    number_by_id = {number.id: number for number in numbers}
    by_number = {
        number.id: {
            "id": number.id,
            "phone": number.phone,
            "sent": 0,
            "received": 0,
            "failed": 0,
            "total": 0,
        }
        for number in visible_numbers
    }
    failures = defaultdict(
        lambda: {
            "failures": 0,
            "last_error": None,
            "last_failure_at": None,
        }
    )
    group_counts = defaultdict(
        lambda: {"total": 0, "sent": 0, "failed": 0}
    )

    for message in messages:
        sender_stats = by_number.get(message.senderId)
        receiver_stats = by_number.get(message.receiverId)
        if sender_stats:
            sender_stats["total"] += 1
            if message.status in {"SENT", "DELIVERED"}:
                sender_stats["sent"] += 1
            elif message.status == "FAILED":
                sender_stats["failed"] += 1
        if receiver_stats and message.status in {"SENT", "DELIVERED"}:
            receiver_stats["received"] += 1

        if message.groupId:
            group_counts[message.groupId]["total"] += 1
            if message.status in {"SENT", "DELIVERED"}:
                group_counts[message.groupId]["sent"] += 1
            elif message.status == "FAILED":
                group_counts[message.groupId]["failed"] += 1

        if message.status == "FAILED":
            failure = failures[message.senderId]
            failure["failures"] += 1
            if failure["last_failure_at"] is None:
                failure["last_error"] = message.error
                failure["last_failure_at"] = message.createdAt

    for number in visible_numbers:
        if number.status == "FAILED" and number.id not in failures:
            failures[number.id]["failures"] = 1

    failed_numbers = []
    for number_id, data in failures.items():
        number = number_by_id.get(number_id)
        if number:
            failed_numbers.append(
                {
                    "id": number.id,
                    "phone": number.phone,
                    **data,
                }
            )
    failed_numbers.sort(key=lambda item: item["failures"], reverse=True)

    warmups = []
    by_group = []
    for group in groups:
        counts = group_counts[group.id]
        pending = counts["total"] - counts["sent"] - counts["failed"]
        by_group.append(
            {
                "id": group.id,
                "name": group.name,
                "member_count": len(group.members),
                "total": counts["total"],
                "sent": counts["sent"],
                "pending": pending,
                "failed": counts["failed"],
            }
        )
        warmups.append(
            {
                "id": group.id,
                "name": group.name,
                "status": group.status,
                "member_count": len(group.members),
                "members": [
                    member.number.phone for member in group.members
                ],
                "started_at": group.startedAt,
                "finish_at": group.finishAt,
                "messages_sent": counts["sent"],
                "messages_failed": counts["failed"],
            }
        )

    sent_messages = sum(
        1 for message in messages if message.status in {"SENT", "DELIVERED"}
    )
    failed_messages = sum(
        1 for message in messages if message.status == "FAILED"
    )

    return {
        "total_messages": len(messages),
        "sent_messages": sent_messages,
        "failed_messages": failed_messages,
        "pending_messages": len(messages) - sent_messages - failed_messages,
        "by_number": sorted(
            by_number.values(),
            key=lambda item: (-item["sent"], item["phone"]),
        ),
        "by_group": by_group,
        "failed_numbers": failed_numbers,
        "warmups": warmups,
    }


async def delete_warmup(group_id: str):
    deleted = await warmup_group_repository.delete_group(group_id)
    if deleted is None:
        raise HTTPException(
            status_code=404,
            detail="Grupo de aquecimento não encontrado",
        )
    return {
        "deleted": True,
        "group_id": group_id,
        "name": deleted.name,
    }
