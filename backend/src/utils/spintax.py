import random
import re

_SPINTAX_PATTERN = re.compile(r"\{([^{}]+)\}")


def parse_spintax(text: str) -> str:
    """Resolve um texto em spintax, ex: '{Oi|Olá|E aí}, tudo {bem|certo}?'
    Suporta aninhamento simples (resolve de dentro para fora)."""
    previous = None
    result = text
    while previous != result:
        previous = result
        result = _SPINTAX_PATTERN.sub(
            lambda m: random.choice(m.group(1).split("|")), result
        )
    return result


# Banco de frases padrão usadas nas conversas de aquecimento.
# Pode ser sobrescrito/ampliado via configuração futura.
DEFAULT_WARMUP_TEMPLATES = [
    "{Oi|Olá|E aí|Opa}, {tudo bem|tudo certo|beleza}?",
    "{Bom dia|Boa tarde|Boa noite}! {Como você está?|Tudo tranquilo por aí?}",
    "{Vi que|Notei que} você {mandou mensagem|chamou} {mais cedo|agora há pouco}, {tudo certo?|precisa de algo?}",
    "{Só passando pra dizer oi|Só dando um alô|Mensagem rápida}: {como estão as coisas?|tudo em ordem?}",
    "{Combinamos aquilo mesmo|Ficou certo então}, {qualquer coisa me avisa|me chama se precisar}.",
    "{Beleza|Show|Perfeito}, {obrigado|valeu}!",
    "{Ok|Certo|Entendido}, {vou verificar|vou dar uma olhada} e {te retorno|falo com você} {daqui a pouco|em breve}.",
]


def random_warmup_message(templates: list[str] | None = None) -> str:
    pool = templates or DEFAULT_WARMUP_TEMPLATES
    return parse_spintax(random.choice(pool))
