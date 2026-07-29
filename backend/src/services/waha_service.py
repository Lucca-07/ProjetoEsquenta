import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from src.utils.logger import logger


class WahaError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class WahaService:
    """Encapsula chamadas HTTP para uma instância WAHA específica.
    Cada 'Number' está associado a um WahaNode (um dos dois servidores KVM8),
    então uma instância deste service é criada com a base_url/api_key
    daquele nó específico."""

    def __init__(
        self, base_url: str, api_key: str | None = None, timeout: float = 30.0
    ):
        self.base_url = base_url.rstrip("/")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["X-Api-Key"] = api_key
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
            logger.error(f"WAHA {method} {self.base_url}{path} inacessível: {exc}")
            raise WahaError(
                f"Não foi possível conectar ao WAHA em {self.base_url} ({exc.__class__.__name__}: {exc})"
            ) from exc

        if response.status_code >= 400:
            logger.error(
                f"WAHA {method} {path} -> {response.status_code}: {response.text}"
            )
            raise WahaError(
                f"WAHA request failed ({response.status_code}): {response.text}",
                status_code=response.status_code,
            )
        return response

    async def start_session(self, session_name: str) -> dict:
        payload = {"name": session_name, "start": True}
        resp = await self._request("POST", "/api/sessions", json=payload)
        return resp.json()

    async def restart_existing_session(self, session_name: str) -> dict:
        payload = {"name": session_name, "start": True}
        resp = await self._request(
            "PUT",
            f"/api/sessions/{session_name}",
            json=payload,
        )
        await self._request(
            "POST",
            f"/api/sessions/{session_name}/start",
        )
        return resp.json()

    async def get_session_status(self, session_name: str) -> dict:
        resp = await self._request("GET", f"/api/sessions/{session_name}")
        return resp.json()

    async def get_qr_code(self, session_name: str) -> str | None:
        try:
            resp = await self._request(
                "GET", f"/api/{session_name}/auth/qr", params={"format": "raw"}
            )
            data = resp.json()
            print(data.get("value"))
            return data.get("value")
        except WahaError:
            return None

    async def stop_session(self, session_name: str) -> dict:
        resp = await self._request("POST", f"/api/sessions/{session_name}/stop")
        return resp.json()

    async def send_text_message(
        self, session_name: str, chat_id: str, text: str
    ) -> dict:
        payload = {"session": session_name, "chatId": chat_id, "text": text}
        resp = await self._request("POST", "/api/sendText", json=payload)
        return resp.json()


def phone_to_chat_id(phone: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())
    return f"{digits}@c.us"


async def build_waha_service_for_node(node) -> WahaService:
    """Recebe um registro WahaNode (do Prisma) e monta o client apontando
    para o servidor correto (kvm8-1 ou kvm8-2)."""
    return WahaService(base_url=node.baseUrl, api_key=node.apiKey)
