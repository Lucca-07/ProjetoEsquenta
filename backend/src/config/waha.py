import json
from pydantic import BaseModel

from src.config.index import settings


class WahaNodeConfig(BaseModel):
    """Um servidor/instância WAHA. Ex: kvm8-1 hospeda parte dos números,
    kvm8-2 hospeda o restante."""

    name: str
    base_url: str
    api_key: str | None = None


def _load_nodes() -> list[WahaNodeConfig]:
    try:
        raw = json.loads(settings.WAHA_NODES)
    except json.JSONDecodeError:
        return []
    return [WahaNodeConfig(**item) for item in raw]


# Exemplo de valor para a env WAHA_NODES:
# WAHA_NODES='[
#   {"name": "kvm8-1", "base_url": "http://127.0.0.1:3000", "api_key": "..."},
#   {"name": "kvm8-2", "base_url": "http://SEU_IP_SERVIDOR_2:3000", "api_key": "..."}
# ]'
waha_nodes: list[WahaNodeConfig] = _load_nodes()


def get_waha_node(name: str) -> WahaNodeConfig | None:
    return next((n for n in waha_nodes if n.name == name), None)
