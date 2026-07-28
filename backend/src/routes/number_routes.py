from fastapi import APIRouter

from src.controllers import number_controller

router = APIRouter(prefix="/numbers", tags=["numbers"])


@router.get("")
async def list_dashboard():
    return await number_controller.list_dashboard()


@router.get("/summary")
async def get_summary():
    return await number_controller.get_summary()
