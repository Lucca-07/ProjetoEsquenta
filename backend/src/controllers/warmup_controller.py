from fastapi import HTTPException

from src.repositories import number_repository, warmup_log_repository
from src.services.warmup_service import calculate_daily_target


async def start_warmup(number_id: str):
    number = await number_repository.get_by_id(number_id)
    if number is None:
        raise HTTPException(status_code=404, detail="Número não encontrado")

    target = calculate_daily_target(number.warmupDay)
    await number_repository.update_warmup_progress(number_id, daily_target=target)
    await number_repository.set_active(number_id, True)
    await warmup_log_repository.add_log(number_id, number.warmupDay, "WARMUP_STARTED")
    return await number_repository.get_by_id(number_id)


async def start_warmup_bulk(number_ids: list[str]):
    return [await start_warmup(number_id) for number_id in number_ids]


async def pause_warmup_bulk(number_ids: list[str]):
    return [await pause_warmup(number_id) for number_id in number_ids]


async def pause_warmup(number_id: str):
    number = await number_repository.get_by_id(number_id)
    if number is None:
        raise HTTPException(status_code=404, detail="Número não encontrado")
    await warmup_log_repository.add_log(number_id, number.warmupDay, "WARMUP_PAUSED")
    return await number_repository.set_active(number_id, False)


async def get_status(number_id: str):
    number = await number_repository.get_by_id(number_id)
    if number is None:
        raise HTTPException(status_code=404, detail="Número não encontrado")
    return {
        "number_id": number.id,
        "phone": number.phone,
        "active": number.active,
        "warmup_day": number.warmupDay,
        "daily_target": number.dailyTarget,
        "daily_sent_count": number.dailySentCount,
        "status": number.status,
    }


async def get_logs(number_id: str):
    number = await number_repository.get_by_id(number_id)
    if number is None:
        raise HTTPException(status_code=404, detail="Número não encontrado")
    return await warmup_log_repository.get_logs_for_number(number_id)
