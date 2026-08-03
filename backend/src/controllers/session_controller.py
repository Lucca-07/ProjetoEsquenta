import asyncio

from fastapi import HTTPException

from src.config.waha import get_waha_node
from src.repositories import number_repository
from src.services.waha_service import WahaError, WahaService, normalize_phone
from src.utils.logger import logger


_session_creation_locks: dict[str, asyncio.Lock] = {}


def _node_config(node_name: str):
    node_cfg = get_waha_node(node_name)
    if node_cfg is None:
        raise HTTPException(
            status_code=400,
            detail=f"Nó WAHA '{node_name}' não configurado",
        )
    return node_cfg


async def create_session(phone: str, node_name: str):
    phone = normalize_phone(phone)
    creation_lock = _session_creation_locks.setdefault(
        phone,
        asyncio.Lock(),
    )
    async with creation_lock:
        return await _create_session_locked(phone, node_name)


async def _create_session_locked(phone: str, node_name: str):
    node_cfg = _node_config(node_name)
    existing = await number_repository.get_by_phone(phone)
    if existing:
        raise HTTPException(
            status_code=409,
            detail="Este número já está cadastrado. Use Reconectar.",
        )

    await number_repository.get_or_create_node(
        node_cfg.name,
        node_cfg.base_url,
        node_cfg.api_key,
    )
    session_name = f"esquenta-{phone}"
    waha = WahaService(node_cfg.base_url, node_cfg.api_key)
    try:
        removed_orphan = False
        for attempt in range(6):
            try:
                await waha.start_session(session_name)
                break
            except WahaError as exc:
                lock_timeout = (
                    exc.status_code == 500
                    and "async-lock timed out" in str(exc)
                )
                if lock_timeout and attempt < 5:
                    logger.warning(
                        f"[session] WAHA ocupado ao criar {session_name}; "
                        f"nova tentativa {attempt + 2}/6"
                    )
                    await asyncio.sleep(2)
                    continue
                if exc.status_code == 422 and not removed_orphan:
                    try:
                        await waha.delete_session(session_name)
                    except WahaError as delete_error:
                        if delete_error.status_code != 404:
                            raise
                    removed_orphan = True
                    await asyncio.sleep(1)
                    continue
                raise
        else:
            raise WahaError(
                f"Tempo esgotado ao iniciar a sessão {session_name}"
            )
    except WahaError as exc:
        logger.error(
            f"[session] falha ao iniciar {session_name}: {exc}"
        )
        raise HTTPException(
            status_code=502,
            detail=(
                "O WAHA não conseguiu iniciar a sessão. "
                "Aguarde alguns segundos e tente novamente."
            ),
        ) from exc
    finally:
        await waha.close()

    return {
        "session_name": session_name,
        "phone": phone,
        "node_name": node_name,
        "status": "STARTING",
    }


async def get_pending_status(
    session_name: str,
    phone: str,
    node_name: str,
):
    phone = normalize_phone(phone)
    node_cfg = _node_config(node_name)
    waha = WahaService(node_cfg.base_url, node_cfg.api_key)
    try:
        status_data = await waha.get_session_status(session_name)
        status = status_data.get("status", "STARTING")
        qr = None
        if status in {"SCAN_QR_CODE", "SCAN_QR"}:
            qr = await waha.get_qr_code(session_name)
        number_id = None
        if status == "WORKING":
            number = await number_repository.get_by_phone(phone)
            if number is None:
                node = await number_repository.get_or_create_node(
                    node_cfg.name,
                    node_cfg.base_url,
                    node_cfg.api_key,
                )
                number = await number_repository.create_number(
                    phone,
                    session_name,
                    node.id,
                )
                logger.info(
                    f"[session] número {phone} confirmado e cadastrado"
                )
            number_id = number.id
        return {
            "session_name": session_name,
            "status": status,
            "qr": qr,
            "number_id": number_id,
        }
    except WahaError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    finally:
        await waha.close()


async def request_pairing_code(
    session_name: str,
    phone: str,
    node_name: str,
):
    node_cfg = _node_config(node_name)
    waha = WahaService(node_cfg.base_url, node_cfg.api_key)
    try:
        ready = False
        restart_requested = False
        for _ in range(20):
            try:
                status_data = await waha.get_session_status(session_name)
                status = status_data.get("status")
                if status in {"SCAN_QR_CODE", "SCAN_QR"}:
                    ready = True
                    break
                if status in {"FAILED", "STOPPED"}:
                    if not restart_requested:
                        logger.warning(
                            f"[session] {session_name} retornou {status}; "
                            "reiniciando antes de gerar o código"
                        )
                        await waha.restart_existing_session(session_name)
                        restart_requested = True
            except WahaError as exc:
                if exc.status_code != 404:
                    logger.warning(
                        f"[session] aguardando sessão {session_name}: {exc}"
                    )
            await asyncio.sleep(1)

        if not ready:
            raise HTTPException(
                status_code=504,
                detail=(
                    "A sessão demorou para ficar pronta. "
                    "Tente gerar o código novamente."
                ),
            )

        code = None
        for attempt in range(6):
            try:
                code = await waha.request_pairing_code(session_name, phone)
                break
            except WahaError as exc:
                transient_webjs_error = (
                    exc.status_code == 500
                    and "reading 'evaluate'" in str(exc)
                )
                if (
                    exc.status_code != 422
                    and not transient_webjs_error
                ) or attempt == 5:
                    raise
                await asyncio.sleep(1)
        return {"code": code}
    except WahaError as exc:
        logger.error(
            f"[session] código de conexão indisponível para "
            f"{session_name}: {exc}"
        )
        raise HTTPException(
            status_code=502,
            detail=(
                "O WAHA não conseguiu gerar o código de conexão. "
                "Tente novamente ou use o QR Code."
            ),
        ) from exc
    finally:
        await waha.close()


async def get_session_status(number_id: str):
    number = await number_repository.get_by_id(number_id)
    if number is None:
        raise HTTPException(status_code=404, detail="Número não encontrado")
    waha = WahaService(number.node.baseUrl, number.node.apiKey)
    try:
        status_data = await waha.get_session_status(number.sessionName)
        status = status_data.get("status", number.status)
        qr = None
        if status in {"SCAN_QR_CODE", "SCAN_QR"}:
            qr = await waha.get_qr_code(number.sessionName)
        if status != number.status:
            await number_repository.update_status(number_id, status)
        return {
            "session_name": number.sessionName,
            "status": status,
            "qr": qr,
            "number_id": number.id,
        }
    finally:
        await waha.close()


async def reconnect_session(number_id: str):
    number = await number_repository.get_by_id(number_id)
    if number is None:
        raise HTTPException(status_code=404, detail="Número não encontrado")
    waha = WahaService(number.node.baseUrl, number.node.apiKey)
    try:
        try:
            await waha.restart_existing_session(number.sessionName)
        except WahaError as exc:
            if exc.status_code != 404:
                raise
            await waha.start_session(number.sessionName)
    except WahaError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao reconectar sessão: {exc}",
        ) from exc
    finally:
        await waha.close()
    await number_repository.mark_reconnecting(number_id)
    return {"number_id": number_id, "status": "STARTING"}


async def list_sessions():
    return await number_repository.list_all()


async def stop_session(number_id: str):
    number = await number_repository.get_by_id(number_id)
    if number is None:
        raise HTTPException(status_code=404, detail="Número não encontrado")
    waha = WahaService(number.node.baseUrl, number.node.apiKey)
    try:
        try:
            await waha.delete_session(number.sessionName)
        except WahaError as exc:
            if exc.status_code != 404:
                raise
    except WahaError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao excluir sessão: {exc}",
        ) from exc
    finally:
        await waha.close()
    deleted = await number_repository.delete_number_with_history(number_id)
    return {"deleted": deleted is not None, "number_id": number_id}
