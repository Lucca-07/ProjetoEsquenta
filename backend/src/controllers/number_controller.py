import asyncio
from datetime import datetime, timezone
from time import monotonic

from src.repositories import number_repository, warmup_group_repository
from src.services.evolution_go_service import EvolutionGoError, EvolutionGoService
from src.utils.logger import logger


_status_refresh_task: asyncio.Task | None = None
_status_refresh_semaphore = asyncio.Semaphore(4)
_last_status_refresh_at = 0.0
_STATUS_REFRESH_INTERVAL_SECONDS = 30


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _progress_percent(number) -> int:
    if number.warmupStartedAt is None or number.warmupFinishAt is None:
        return 0

    inicio = number.warmupStartedAt
    fim = number.warmupFinishAt
    agora = _now_utc()

    duracao_total = (fim - inicio).total_seconds()

    if duracao_total <= 0:
        return 100

    tempo_decorrido = (agora - inicio).total_seconds()
    pct = round((tempo_decorrido / duracao_total) * 100)

    return max(0, min(100, pct))


def _remaining_label(number) -> str:
    if number.warmupFinishAt is None:
        return "0min"

    segundos_restantes = (
        number.warmupFinishAt - _now_utc()
    ).total_seconds()

    if segundos_restantes <= 0:
        return "Concluído"

    dias = int(segundos_restantes // 86400)
    horas = int((segundos_restantes % 86400) // 3600)
    minutos = int((segundos_restantes % 3600) // 60)

    if dias > 0:
        return f"{dias}d {horas}h"

    if horas > 0:
        return f"{horas}h {minutos}min"

    return f"{max(1, minutos)}min"


def _is_completed(number) -> bool:
    return (
        number.warmupFinishAt is not None
        and _now_utc() >= number.warmupFinishAt
    )


def _status_label(number) -> str:
    if number.status == "FAILED":
        return "Falhou"

    if number.status == "STOPPED":
        return "Desconectado"

    if number.warmupStartedAt is None or number.warmupFinishAt is None:
        return "Sem ação"

    if _is_completed(number):
        return "Concluído"

    if not number.active:
        return "Pausado"

    if number.status != "WORKING":
        return "Conectando"

    return "Esquentando"


def _to_dashboard_item(number, group_name: str | None = None) -> dict:
    return {
        "id": number.id,
        "numero": number.phone,
        "progresso": _progress_percent(number),
        "tempo_restante": _remaining_label(number),
        "status": _status_label(number),
        "grupo": group_name or "—",
        "conectado": number.status == "WORKING",
    }


async def list_dashboard():
    numbers = await number_repository.list_all()
    _schedule_status_refresh(numbers)
    groups = await warmup_group_repository.list_active()
    group_names = {
        member.numberId: group.name
        for group in groups
        for member in group.members
    }
    return [_to_dashboard_item(n, group_names.get(n.id)) for n in numbers]


def _schedule_status_refresh(numbers) -> None:
    global _last_status_refresh_at, _status_refresh_task

    refresh_due = (
        monotonic() - _last_status_refresh_at
        >= _STATUS_REFRESH_INTERVAL_SECONDS
    )
    if refresh_due and (
        _status_refresh_task is None or _status_refresh_task.done()
    ):
        _last_status_refresh_at = monotonic()
        _status_refresh_task = asyncio.create_task(
            _refresh_all_session_statuses(numbers)
        )


async def _refresh_all_session_statuses(numbers) -> None:
    async def refresh_with_limit(number) -> None:
        async with _status_refresh_semaphore:
            await _refresh_session_status(number)

    await asyncio.gather(
        *(refresh_with_limit(number) for number in numbers)
    )


async def _refresh_session_status(number) -> None:
    evolution = EvolutionGoService(number.node.baseUrl, number.node.apiKey)
    try:
        status = await evolution.get_instance_status(number.sessionName)
        if status != number.status:
            await number_repository.update_status(number.id, status)
            number.status = status
    except EvolutionGoError as exc:
        logger.warning(
            f"[session] Não foi possível atualizar o status de "
            f"{number.phone}: {exc}"
        )
    finally:
        await evolution.close()


async def get_summary():
    numbers = await number_repository.list_all()

    connected = sum(
        1 for n in numbers
        if n.status == "WORKING"
    )

    warming = sum(
        1 for n in numbers
        if (
            n.active
            and n.status == "WORKING"
            and not _is_completed(n)
        )
    )

    completed = sum(
        1 for n in numbers
        if _is_completed(n)
    )

    not_completed = sum(
        1 for n in numbers
        if n.status == "FAILED" or (
            not n.active and not _is_completed(n)
        )
    )

    return {
        "connected": connected,
        "warming": warming,
        "completed": completed,
        "not_completed": not_completed,
        "total": len(numbers),
    }
