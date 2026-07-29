from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from src.models.warmup_schema import WarmupBulkRequest
from src.repositories import number_repository, warmup_log_repository
from src.services.warmup_service import calculate_daily_target


async def start_warmup(
    number_id: str,
    interval_seconds: int,
    duration_hours: int,
):
    number = await number_repository.get_by_id(number_id)

    if number is None:
        raise HTTPException(
            status_code=404,
            detail="Número não encontrado",
        )

    target = calculate_daily_target(number.warmupDay)

    await number_repository.update_warmup_progress(
        number_id,
        daily_target=target,
    )

    agora = datetime.now(timezone.utc)

    await number_repository.update_warmup_config(
        number_id=number_id,
        interval_seconds=interval_seconds,
        duration_hours=duration_hours,
        warmup_started_at=agora,
        warmup_finish_at=agora + timedelta(hours=duration_hours),
    )

    await number_repository.set_active(number_id, True)

    await warmup_log_repository.add_log(
        number_id,
        number.warmupDay,
        "WARMUP_STARTED",
    )

    return await number_repository.get_by_id(number_id)


async def start_warmup_bulk(payload: WarmupBulkRequest):
    resultado = []

    for number_id in payload.number_ids:
        resultado.append(
            await start_warmup(
                number_id,
                payload.interval_seconds,
                payload.duration_hours,
            )
        )

    return resultado


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
