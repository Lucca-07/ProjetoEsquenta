from fastapi import APIRouter, Depends, Query

from src.controllers import dashboard_log_controller
from src.services.auth_service import require_admin


router = APIRouter(
    prefix="/logs",
    tags=["logs"],
    dependencies=[Depends(require_admin)],
)


@router.get("/dashboard")
async def get_dashboard(
    days: int | None = Query(None, ge=1, le=365),
    phone: str | None = Query(None, max_length=30),
    status: str | None = Query(None, pattern="^(ACTIVE|COMPLETED|STOPPED)$"),
):
    return await dashboard_log_controller.get_dashboard(days, phone, status)


@router.delete("/warmups/{group_id}")
async def delete_warmup(group_id: str):
    return await dashboard_log_controller.delete_warmup(group_id)
