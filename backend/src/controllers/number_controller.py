from src.config.index import settings
from src.repositories import number_repository


def _progress_percent(number) -> int:
    if settings.WARMUP_MAX_DAYS <= 0:
        return 0
    pct = round((number.warmupDay / settings.WARMUP_MAX_DAYS) * 100)
    return max(0, min(100, pct))


def _remaining_label(number) -> str:
    remaining_days = max(0, settings.WARMUP_MAX_DAYS - number.warmupDay)
    if remaining_days == 0:
        return "Concluído"
    if remaining_days == 1:
        return "1 dia"
    return f"{remaining_days} dias"


def _status_label(number) -> str:
    if number.status == "FAILED":
        return "Falhou"
    if not number.active:
        return "Pausado"
    if number.status != "WORKING":
        return "Conectando"
    if number.warmupDay >= settings.WARMUP_MAX_DAYS:
        return "Concluído"
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
    connected = sum(1 for n in numbers if n.status == "WORKING")
    warming = sum(
        1 for n in numbers
        if n.active and n.status == "WORKING" and n.warmupDay < settings.WARMUP_MAX_DAYS
    )
    completed = sum(1 for n in numbers if n.warmupDay >= settings.WARMUP_MAX_DAYS)
    not_completed = sum(1 for n in numbers if n.status == "FAILED" or not n.active)
    return {
        "connected": connected,
        "warming": warming,
        "completed": completed,
        "not_completed": not_completed,
        "total": len(numbers),
    }
