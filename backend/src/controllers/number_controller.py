from datetime import datetime, timezone

from src.repositories import number_repository


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

    return "Em andamento"


def _to_dashboard_item(number) -> dict:
    return {
        "id": number.id,
        "numero": number.phone,
        "progresso": _progress_percent(number),
        "tempo_restante": _remaining_label(number),
        "status": _status_label(number),
        "conectado": number.status == "WORKING",
    }


async def list_dashboard():
    numbers = await number_repository.list_all()
    return [_to_dashboard_item(n) for n in numbers]


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
