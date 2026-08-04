import hashlib
import hmac
import json
import uuid

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.utils.logger import logger


class EvolutionGoError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class EvolutionGoService:
    """HTTP client for one Evolution Go server."""

    def __init__(self, base_url: str, api_key: str | None = None, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or ""
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Content-Type": "application/json", "apikey": self.api_key},
            timeout=timeout,
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
            logger.error(f"Evolution Go {method} {self.base_url}{path} inaccessible: {exc}")
            raise EvolutionGoError(
                f"Nao foi possivel conectar a Evolution Go em {self.base_url} "
                f"({exc.__class__.__name__}: {exc})"
            ) from exc

        if response.status_code >= 400:
            logger.error(
                f"Evolution Go {method} {path} -> {response.status_code}: {response.text}"
            )
            raise EvolutionGoError(
                f"Evolution Go request failed ({response.status_code}): {response.text}",
                status_code=response.status_code,
            )
        return response

    def _instance_headers(self, instance_name: str) -> dict[str, str]:
        return {"apikey": evolution_go_instance_token(self.api_key, instance_name)}

    async def create_instance(
        self, instance_name: str, phone: str | None = None
    ) -> dict:
        payload = {
            "instanceId": evolution_go_instance_id(instance_name),
            "name": instance_name,
            "token": evolution_go_instance_token(self.api_key, instance_name),
        }
        response = await self._request("POST", "/instance/create", json=payload)
        return response.json()

    async def restart_instance(self, instance_name: str) -> dict:
        response = await self._request(
            "POST",
            "/instance/reconnect",
            headers=self._instance_headers(instance_name),
        )
        return response.json() if response.content else {}

    async def delete_instance(self, instance_name: str) -> dict:
        instance_id = evolution_go_instance_id(instance_name)
        response = await self._request("DELETE", f"/instance/delete/{instance_id}")
        return response.json() if response.content else {}

    async def request_pairing_code(self, instance_name: str, phone: str) -> str:
        response = await self._request(
            "POST",
            "/instance/pair",
            headers=self._instance_headers(instance_name),
            json={"phone": normalize_phone(phone)},
        )
        data = response.json().get("data") or {}
        code = data.get("PairingCode") or data.get("pairingCode")
        if not code:
            raise EvolutionGoError("A Evolution Go nao retornou um codigo de conexao")
        return code

    async def get_instance_status(self, instance_name: str) -> str:
        response = await self._request(
            "GET", "/instance/status", headers=self._instance_headers(instance_name)
        )
        data = response.json().get("data") or {}
        connected = data.get("Connected", data.get("connected", False))
        logged_in = data.get("LoggedIn", data.get("loggedIn", False))
        return normalize_evolution_status(connected, logged_in)

    async def get_qr_code(self, instance_name: str) -> str | None:
        try:
            response = await self._request(
                "GET", "/instance/qr", headers=self._instance_headers(instance_name)
            )
        except EvolutionGoError:
            return None
        data = response.json().get("data") or {}
        return data.get("code") or data.get("Code")

    async def send_text_message(self, instance_name: str, phone: str, text: str) -> dict:
        payload = {"number": normalize_phone(phone), "text": text}
        response = await self._request(
            "POST",
            "/send/text",
            headers=self._instance_headers(instance_name),
            json=payload,
        )
        return response.json()


def normalize_phone(phone: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) in {10, 11}:
        digits = f"55{digits}"
    return digits


def evolution_go_instance_id(instance_name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"esquenta:{instance_name}"))


def evolution_go_instance_token(api_key: str, instance_name: str) -> str:
    return hmac.new(
        api_key.encode("utf-8"), instance_name.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def normalize_evolution_status(connected: bool, logged_in: bool) -> str:
    if logged_in:
        return "WORKING"
    if connected:
        return "SCAN_QR_CODE"
    return "STOPPED"


def extract_message_id(result: dict) -> str | None:
    data = result.get("data") or result
    info = data.get("Info") or data.get("info") or {}
    message_id = info.get("ID") or info.get("id") or data.get("id")
    if isinstance(message_id, str):
        return message_id
    if message_id is not None:
        return json.dumps(message_id, ensure_ascii=False, separators=(",", ":"))
    return None


async def build_evolution_go_service_for_node(node) -> EvolutionGoService:
    return EvolutionGoService(base_url=node.baseUrl, api_key=node.apiKey)
