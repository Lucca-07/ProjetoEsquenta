import json

from pydantic import BaseModel

from src.config.index import settings


class EvolutionGoNodeConfig(BaseModel):
    name: str
    base_url: str
    api_key: str | None = None


def _load_nodes() -> list[EvolutionGoNodeConfig]:
    try:
        raw = json.loads(settings.EVOLUTION_GO_NODES)
    except json.JSONDecodeError:
        return []
    return [EvolutionGoNodeConfig(**item) for item in raw]


evolution_go_nodes: list[EvolutionGoNodeConfig] = _load_nodes()


def get_evolution_go_node(name: str) -> EvolutionGoNodeConfig | None:
    return next((node for node in evolution_go_nodes if node.name == name), None)
