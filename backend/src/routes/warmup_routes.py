from fastapi import APIRouter

from src.controllers import warmup_controller
from src.models.warmup_schema import WarmupStatusResponse

router = APIRouter(prefix="/warmup", tags=["warmup"])


@router.post("/{number_id}/start")
async def start_warmup(number_id: str):
    return await warmup_controller.start_warmup(number_id)


@router.post("/{number_id}/pause")
async def pause_warmup(number_id: str):
    return await warmup_controller.pause_warmup(number_id)


@router.get("/{number_id}/status", response_model=WarmupStatusResponse)
async def get_status(number_id: str):
    return await warmup_controller.get_status(number_id)


@router.get("/{number_id}/logs")
async def get_logs(number_id: str):
    return await warmup_controller.get_logs(number_id)
