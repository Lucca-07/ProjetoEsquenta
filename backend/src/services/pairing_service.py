import random

from src.repositories import warmup_group_repository


async def get_group_for(number):
    return await warmup_group_repository.get_active_for_number(number.id)


async def get_partner_for(number) -> object | None:
    """Escolhe outro número ativo exclusivamente dentro do mesmo esquenta."""
    group = await get_group_for(number)
    if group is None:
        return None

    candidates = [
        member.number
        for member in group.members
        if (
            member.numberId != number.id
            and member.number.active
            and member.number.status == "WORKING"
            and member.number.warmupStartedAt is not None
            and member.number.warmupFinishAt is not None
        )
    ]
    return random.choice(candidates) if candidates else None
