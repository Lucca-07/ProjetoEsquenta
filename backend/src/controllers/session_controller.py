from fastapi import HTTPException

from src.config.waha import get_waha_node
from src.repositories import number_repository
from src.services.waha_service import WahaService, WahaError
from src.utils.logger import logger


async def create_session(phone: str, node_name: str):
    node_cfg = get_waha_node(node_name)
    if node_cfg is None:
        raise HTTPException(status_code=400, detail=f"Nó WAHA '{node_name}' não configurado")

    node = await number_repository.get_or_create_node(node_cfg.name, node_cfg.base_url, node_cfg.api_key)

    session_name = f"esquenta-{phone}"
    existing = await number_repository.get_by_session_name(session_name)
    if existing:
        if existing.status != "STOPPED":
            raise HTTPException(status_code=409, detail="Já existe uma sessão para esse número")

        waha = WahaService(
            base_url=existing.node.baseUrl,
            api_key=existing.node.apiKey,
        )
        try:
            await waha.restart_existing_session(session_name)
        except WahaError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"Falha ao reconectar sessão no WAHA: {exc}",
            ) from exc
        finally:
            await waha.close()

        logger.info(f"[session] reconectando sessão {session_name}")
        return await number_repository.mark_reconnecting(existing.id)

    waha = WahaService(base_url=node.baseUrl, api_key=node.apiKey)
    try:
        try:
            await waha.start_session(session_name)
        except WahaError as exc:
            if exc.status_code != 422 or "already exists" not in str(exc):
                raise

            logger.info(
                f"[session] recuperando sessão existente {session_name} no WAHA"
            )
            await waha.restart_existing_session(session_name)
    except WahaError as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao iniciar sessão no WAHA: {exc}") from exc
    finally:
        await waha.close()

    number = await number_repository.create_number(phone, session_name, node.id)
    logger.info(f"[session] sessão criada para {phone} no nó {node.name}")
    return number


async def get_session_status(number_id: str):
    number = await number_repository.get_by_id(number_id)
    if number is None:
        raise HTTPException(status_code=404, detail="Número não encontrado")

    waha = WahaService(base_url=number.node.baseUrl, api_key=number.node.apiKey)
    try:
        status_data = await waha.get_session_status(number.sessionName)
        status = status_data.get("status", number.status)
        qr = None
        if status == "SCAN_QR_CODE":
            qr = await waha.get_qr_code(number.sessionName)
        if status != number.status:
            await number_repository.update_status(number_id, status)
        return {"session_name": number.sessionName, "status": status, "qr": qr}
    finally:
        await waha.close()


async def list_sessions():
    return await number_repository.list_all()


async def stop_session(number_id: str):
    number = await number_repository.get_by_id(number_id)
    if number is None:
        raise HTTPException(status_code=404, detail="Número não encontrado")

    waha = WahaService(base_url=number.node.baseUrl, api_key=number.node.apiKey)
    try:
        await waha.stop_session(number.sessionName)
    except WahaError as exc:
        raise HTTPException(status_code=502, detail=f"Falha ao parar sessão: {exc}") from exc
    finally:
        await waha.close()

    deleted_number = await number_repository.delete_number_with_history(number_id)
    return {
        "deleted": deleted_number is not None,
        "number_id": number_id,
    }
