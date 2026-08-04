import json

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.utils.logger import logger


class EvolutionError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class EvolutionService:
    """HTTP client for one Evolution API server."""

    def __init__(self, base_url: str, api_key: str | None = None, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["apikey"] = api_key
        self._client = httpx.AsyncClient(
            base_url=self.base_url, headers=headers, timeout=timeout
        )

    async def close(self):
        await self._client.aclose()

    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(httpx.TransportError),
    )
    async def _do_request(self, method: str, path: str, **kwargs) -> httpx.Response:
        return await self._client.request(method, path, **kwargs)

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        try:
            response = await self._do_request(method, path, **kwargs)
        except httpx.TransportError as exc:
            logger.error(f"Evolution {method} {self.base_url}{path} inaccessible: {exc}")
            raise EvolutionError(
                f"Nao foi possivel conectar a Evolution API em {self.base_url} "
                f"({exc.__class__.__name__}: {exc})"
            ) from exc

        if response.status_code >= 400:
            logger.error(
                f"Evolution {method} {path} -> {response.status_code}: {response.text}"
            )
            raise EvolutionError(
                f"Evolution request failed ({response.status_code}): {response.text}",
                status_code=response.status_code,
            )
        return response

    async def create_instance(self, instance_name: str) -> dict:
        payload = {
            "instanceName": instance_name,
            "integration": "WHATSAPP-BAILEYS",
            "qrcode": True,
        }
        response = await self._request("POST", "/instance/create", json=payload)
        return response.json()

    async def restart_instance(self, instance_name: str) -> dict:
        response = await self._request("PUT", f"/instance/restart/{instance_name}")
        return response.json() if response.content else {}

    async def delete_instance(self, instance_name: str) -> dict:
        response = await self._request("DELETE", f"/instance/delete/{instance_name}")
        return response.json() if response.content else {}

    async def connect_instance(self, instance_name: str, phone: str | None = None) -> dict:
        params = {"number": normalize_phone(phone)} if phone else None
        response = await self._request(
            "GET", f"/instance/connect/{instance_name}", params=params
        )
        return response.json()

    async def request_pairing_code(self, instance_name: str, phone: str) -> str:
        data = await self.connect_instance(instance_name, phone)
        code = data.get("pairingCode") or data.get("pairing_code")
        if not code:
            raise EvolutionError("A Evolution API nao retornou um codigo de conexao")
        return code

    async def get_instance_status(self, instance_name: str) -> str:
        response = await self._request(
            "GET", f"/instance/connectionState/{instance_name}"
        )
        data = response.json()
        instance = data.get("instance") or {}
        return normalize_evolution_status(instance.get("state") or data.get("state"))

    async def get_qr_code(self, instance_name: str) -> str | None:
        try:
            data = await self.connect_instance(instance_name)
        except EvolutionError:
            return None
        qrcode = data.get("qrcode")
        if isinstance(qrcode, dict):
            qrcode = qrcode.get("code")
        return data.get("code") or qrcode

    async def send_text_message(self, instance_name: str, phone: str, text: str) -> dict:
        payload = {"number": normalize_phone(phone), "text": text}
        response = await self._request(
            "POST", f"/message/sendText/{instance_name}", json=payload
        )
        return response.json()


def normalize_phone(phone: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) in {10, 11}:
        digits = f"55{digits}"
    return digits


def normalize_evolution_status(state: str | None) -> str:
    normalized = (state or "").lower()
    return {
        "open": "WORKING",
        "connecting": "SCAN_QR_CODE",
        "close": "STOPPED",
        "closed": "STOPPED",
    }.get(normalized, "STARTING")


def extract_message_id(result: dict) -> str | None:
    key = result.get("key")
    if isinstance(key, dict) and isinstance(key.get("id"), str):
        return key["id"]

    message_id = result.get("id")
    if isinstance(message_id, str):
        return message_id
    if message_id is not None:
        return json.dumps(message_id, ensure_ascii=False, separators=(",", ":"))
    return None


async def build_evolution_service_for_node(node) -> EvolutionService:
    return EvolutionService(base_url=node.baseUrl, api_key=node.apiKey)
