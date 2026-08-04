from fastapi import APIRouter

from src.controllers import session_controller
from src.models.session_schema import (
    SessionCreate,
    PairingCodeRequest,
    PendingSessionResponse,
    SessionResponse,
    SessionStatusResponse,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=PendingSessionResponse, status_code=201)
async def create_session(payload: SessionCreate):
    return await session_controller.create_session(
        payload.phone,
        payload.node_name,
        payload.connection_method,
    )


@router.get("")
async def list_sessions():
    return await session_controller.list_sessions()


@router.get("/{number_id}/status", response_model=SessionStatusResponse)
async def get_session_status(number_id: str):
    return await session_controller.get_session_status(number_id)


@router.get(
    "/pending/{session_name}/status",
    response_model=SessionStatusResponse,
)
async def get_pending_status(
    session_name: str,
    phone: str,
    node_name: str,
    connection_method: str = "qr",
):
    return await session_controller.get_pending_status(
        session_name,
        phone,
        node_name,
        connection_method,
    )


@router.post("/pending/{session_name}/code")
async def request_pairing_code(
    session_name: str,
    payload: PairingCodeRequest,
):
    return await session_controller.request_pairing_code(
        session_name,
        payload.phone,
        payload.node_name,
    )


@router.post("/{number_id}/reconnect")
async def reconnect_session(number_id: str):
    return await session_controller.reconnect_session(number_id)


@router.post("/{number_id}/stop")
async def stop_session(number_id: str):
    return await session_controller.stop_session(number_id)
