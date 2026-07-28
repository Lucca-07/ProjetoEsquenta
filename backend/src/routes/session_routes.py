from fastapi import APIRouter

from src.controllers import session_controller
from src.models.session_schema import SessionCreate, SessionResponse, SessionStatusResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(payload: SessionCreate):
    number = await session_controller.create_session(payload.phone, payload.node_name)
    return SessionResponse(
        id=number.id,
        phone=number.phone,
        session_name=number.sessionName,
        node_name=payload.node_name,
        status=number.status,
        active=number.active,
        warmup_day=number.warmupDay,
        daily_target=number.dailyTarget,
        daily_sent_count=number.dailySentCount,
        created_at=number.createdAt,
    )


@router.get("")
async def list_sessions():
    return await session_controller.list_sessions()


@router.get("/{number_id}/status", response_model=SessionStatusResponse)
async def get_session_status(number_id: str):
    return await session_controller.get_session_status(number_id)


@router.post("/{number_id}/stop")
async def stop_session(number_id: str):
    return await session_controller.stop_session(number_id)
