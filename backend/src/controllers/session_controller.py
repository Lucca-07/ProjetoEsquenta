import asyncio

from fastapi import HTTPException

from src.config.evolution_go import get_evolution_go_node
from src.repositories import number_repository
from src.services.evolution_go_service import EvolutionGoError, EvolutionGoService, normalize_phone
from src.utils.logger import logger


_instance_creation_locks: dict[str, asyncio.Lock] = {}
_pending_status_locks: dict[str, asyncio.Lock] = {}


def _node_config(node_name: str):
    node_cfg = get_evolution_go_node(node_name)
    if node_cfg is None:
        raise HTTPException(
            status_code=400,
            detail=f"No Evolution '{node_name}' nao configurado",
        )
    return node_cfg


async def create_session(
    phone: str, node_name: str, connection_method: str = "qr"
):
    phone = normalize_phone(phone)
    creation_lock = _instance_creation_locks.setdefault(phone, asyncio.Lock())
    async with creation_lock:
        return await _create_session_locked(phone, node_name, connection_method)


async def _create_session_locked(
    phone: str, node_name: str, connection_method: str
):
    node_cfg = _node_config(node_name)
    existing = await number_repository.get_by_phone(phone)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Este numero ja esta cadastrado. Use Reconectar.",
        )

    await number_repository.get_or_create_node(
        node_cfg.name, node_cfg.base_url, node_cfg.api_key
    )
    instance_name = phone
    evolution = EvolutionGoService(node_cfg.base_url, node_cfg.api_key)
    try:
        try:
            await evolution.create_instance(
                instance_name,
                phone if connection_method == "code" else None,
            )
        except EvolutionGoError as exc:
            instance_exists = (
                exc.status_code in {403, 409, 422}
                or "already exists" in str(exc).lower()
            )
            if not instance_exists:
                raise
            logger.info(
                f"[instance] {instance_name} ja existe; reutilizando para pareamento"
            )
    except EvolutionGoError as exc:
        logger.error(f"[instance] falha ao criar {instance_name}: {exc}")
        raise HTTPException(
            status_code=502,
            detail=(
                "A Evolution Go nao conseguiu criar a instancia. "
                "Aguarde alguns segundos e tente novamente."
            ),
        ) from exc
    finally:
        await evolution.close()

    return {
        "session_name": instance_name,
        "phone": phone,
        "node_name": node_name,
        "status": "STARTING",
    }


async def get_pending_status(
    session_name: str,
    phone: str,
    node_name: str,
    connection_method: str = "qr",
):
    lock_key = f"{node_name}:{session_name}"
    status_lock = _pending_status_locks.setdefault(lock_key, asyncio.Lock())
    async with status_lock:
        return await _get_pending_status_locked(
            session_name, phone, node_name, connection_method
        )


async def _get_pending_status_locked(
    session_name: str,
    phone: str,
    node_name: str,
    connection_method: str,
):
    phone = normalize_phone(phone)
    node_cfg = _node_config(node_name)
    evolution = EvolutionGoService(node_cfg.base_url, node_cfg.api_key)
    try:
        status = await evolution.get_instance_status(session_name)
        qr = None
        if connection_method == "qr" and status in {
            "STARTING",
            "SCAN_QR_CODE",
            "STOPPED",
        }:
            qr = await evolution.get_qr_code(session_name)
            if qr:
                status = "SCAN_QR_CODE"

        number_id = None
        if status == "WORKING":
            number = await number_repository.get_by_phone(phone)
            if number is None:
                node = await number_repository.get_or_create_node(
                    node_cfg.name, node_cfg.base_url, node_cfg.api_key
                )
                number = await number_repository.create_number(
                    phone, session_name, node.id
                )
                logger.info(f"[instance] numero {phone} confirmado e cadastrado")
            number_id = number.id

        return {
            "session_name": session_name,
            "status": status,
            "qr": qr,
            "number_id": number_id,
        }
    except EvolutionGoError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        await evolution.close()


async def request_pairing_code(session_name: str, phone: str, node_name: str):
    node_cfg = _node_config(node_name)
    evolution = EvolutionGoService(node_cfg.base_url, node_cfg.api_key)
    try:
        for attempt in range(30):
            try:
                code = await evolution.request_pairing_code(session_name, phone)
                return {"code": code}
            except EvolutionGoError as exc:
                license_error = "license" in str(exc).lower()
                retryable = (
                    exc.status_code in {None, 404, 409, 422, 500, 503}
                    and not license_error
                )
                if not retryable:
                    raise
                if attempt == 29:
                    raise
                await asyncio.sleep(1)
    except EvolutionGoError as exc:
        logger.error(
            f"[instance] codigo de conexao indisponivel para {session_name}: {exc}"
        )
        raise HTTPException(
            status_code=502,
            detail=(
                "A Evolution Go nao conseguiu gerar o codigo de conexao. "
                "Tente novamente ou use o QR Code."
            ),
        ) from exc
    finally:
        await evolution.close()


async def get_session_status(number_id: str):
    number = await number_repository.get_by_id(number_id)
    if number is None:
        raise HTTPException(status_code=404, detail="Numero nao encontrado")
    evolution = EvolutionGoService(number.node.baseUrl, number.node.apiKey)
    try:
        status = await evolution.get_instance_status(number.sessionName)
        qr = None
        if status in {"STARTING", "SCAN_QR_CODE", "STOPPED"}:
            qr = await evolution.get_qr_code(number.sessionName)
        if status != number.status:
            await number_repository.update_status(number_id, status)
        return {
            "session_name": number.sessionName,
            "status": status,
            "qr": qr,
            "number_id": number.id,
        }
    finally:
        await evolution.close()


async def reconnect_session(number_id: str):
    number = await number_repository.get_by_id(number_id)
    if number is None:
        raise HTTPException(status_code=404, detail="Numero nao encontrado")
    evolution = EvolutionGoService(number.node.baseUrl, number.node.apiKey)
    try:
        try:
            await evolution.restart_instance(number.sessionName)
        except EvolutionGoError as exc:
            if exc.status_code not in {401, 404}:
                raise
            await evolution.create_instance(number.sessionName)
    except EvolutionGoError as exc:
        raise HTTPException(
            status_code=502, detail=f"Falha ao reconectar instancia: {exc}"
        ) from exc
    finally:
        await evolution.close()
    await number_repository.mark_reconnecting(number_id)
    return {"number_id": number_id, "status": "STARTING"}


async def list_sessions():
    return await number_repository.list_all()


async def stop_session(number_id: str):
    number = await number_repository.get_by_id(number_id)
    if number is None:
        raise HTTPException(status_code=404, detail="Numero nao encontrado")
    evolution = EvolutionGoService(number.node.baseUrl, number.node.apiKey)
    try:
        try:
            await evolution.delete_instance(number.sessionName)
        except EvolutionGoError as exc:
            instance_missing = (
                exc.status_code in {401, 404}
                or "record not found" in str(exc).lower()
            )
            if not instance_missing:
                raise
    except EvolutionGoError as exc:
        raise HTTPException(
            status_code=502, detail=f"Falha ao excluir instancia: {exc}"
        ) from exc
    finally:
        await evolution.close()
    deleted = await number_repository.delete_number_with_history(number_id)
    return {"deleted": deleted is not None, "number_id": number_id}
