import json

from pydantic import BaseModel

from src.config.index import settings


class EvolutionNodeConfig(BaseModel):
    name: str
    base_url: str
    api_key: str | None = None


def _load_nodes() -> list[EvolutionNodeConfig]:
    try:
        raw = json.loads(settings.EVOLUTION_NODES)
    except json.JSONDecodeError:
        return []
    return [EvolutionNodeConfig(**item) for item in raw]


evolution_nodes: list[EvolutionNodeConfig] = _load_nodes()


def get_evolution_node(name: str) -> EvolutionNodeConfig | None:
    return next((node for node in evolution_nodes if node.name == name), None)
