from datetime import datetime, timedelta, timezone

from fastapi import HTTPException

from src.models.warmup_schema import WarmupBulkRequest
from src.repositories import (
    number_repository,
    warmup_group_repository,
    warmup_log_repository,
)
from src.services.warmup_service import calculate_daily_target
from src.utils.logger import logger


async def start_warmup(
    number_id: str,
    interval_seconds: int = 240,
    duration_hours: int = 24,
):
    number = await number_repository.get_by_id(number_id)

    if number is None:
        raise HTTPException(
            status_code=404,
            detail="Número não encontrado",
        )

    await warmup_log_repository.cancel_pending_for_sender(number_id)

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
    unique_ids = list(dict.fromkeys(payload.number_ids))
    if len(unique_ids) < 2:
        raise HTTPException(
            status_code=422,
            detail="Um esquenta em grupo precisa de pelo menos dois números",
        )

    numbers = []
    for number_id in unique_ids:
        number = await number_repository.get_by_id(number_id)
        if number is None:
            raise HTTPException(status_code=404, detail="Número não encontrado")
        if number.status != "WORKING":
            raise HTTPException(
                status_code=409,
                detail=f"O número {number.phone} não está conectado",
            )
        active_group = await warmup_group_repository.get_active_for_number(
            number_id
        )
        if active_group:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"O número {number.phone} já pertence ao esquenta "
                    f"'{active_group.name}'"
                ),
            )
        numbers.append(number)

    agora = datetime.now(timezone.utc)
    group = await warmup_group_repository.create_group(
        payload.name,
        unique_ids,
        payload.interval_seconds,
        payload.duration_hours,
        agora,
        agora + timedelta(hours=payload.duration_hours),
    )

    resultado = []

    for number_id in unique_ids:
        resultado.append(
            await start_warmup(
                number_id,
                payload.interval_seconds,
                payload.duration_hours,
            )
        )

    return {
        "id": group.id,
        "name": group.name,
        "status": group.status,
        "member_count": len(unique_ids),
        "numbers": resultado,
    }


async def pause_warmup_bulk(number_ids: list[str]):
    expanded_ids = await _expand_group_members(number_ids)
    return [await pause_warmup(number_id) for number_id in expanded_ids]


async def stop_warmup_bulk(number_ids: list[str]):
    expanded_ids = await _expand_group_members(number_ids)
    return [await stop_warmup(number_id) for number_id in expanded_ids]


async def _expand_group_members(number_ids: list[str]) -> list[str]:
    """Expande qualquer integrante selecionado para todo o seu grupo ativo."""
    expanded = set(number_ids)
    for number_id in number_ids:
        group = await warmup_group_repository.get_active_for_number(number_id)
        if group:
            expanded.update(member.numberId for member in group.members)
    return list(expanded)


async def pause_warmup(number_id: str):
    number = await number_repository.get_by_id(number_id)
    if number is None:
        raise HTTPException(status_code=404, detail="Número não encontrado")
    await warmup_log_repository.add_log(number_id, number.warmupDay, "WARMUP_PAUSED")
    return await number_repository.set_active(number_id, False)


async def stop_warmup(number_id: str):
    number = await number_repository.get_by_id(number_id)
    if number is None:
        raise HTTPException(status_code=404, detail="Número não encontrado")

    active_group = await warmup_group_repository.get_active_for_number(
        number_id
    )
    stopped_number = await number_repository.stop_warmup(number_id)

    if active_group:
        refreshed_group = await warmup_group_repository.get_by_id(
            active_group.id
        )
        if not any(member.number.active for member in refreshed_group.members):
            await warmup_group_repository.set_status(
                active_group.id,
                "STOPPED",
            )

    try:
        await warmup_log_repository.add_log(
            number_id,
            number.warmupDay,
            "WARMUP_STOPPED",
        )
    except Exception:
        logger.exception(
            "[warmup] Aquecimento parado, mas não foi possível registrar o log "
            f"do número {number_id}"
        )

    return stopped_number


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
