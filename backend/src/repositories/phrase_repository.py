from src.db import db


async def list_phrases(active_only: bool = True, category: str | None = None):
    where: dict = {}
    if active_only:
        where["active"] = True
    if category:
        where["category"] = category
    return await db.warmupphrase.find_many(where=where, order={"createdAt": "asc"})


async def create_phrase(text: str, category: str = "geral"):
    return await db.warmupphrase.create(data={"text": text, "category": category})


async def get_phrase(phrase_id: str):
    return await db.warmupphrase.find_unique(where={"id": phrase_id})


async def update_phrase(phrase_id: str, text: str | None = None, category: str | None = None,
                         active: bool | None = None):
    data: dict = {}
    if text is not None:
        data["text"] = text
    if category is not None:
        data["category"] = category
    if active is not None:
        data["active"] = active
    if not data:
        return await get_phrase(phrase_id)
    return await db.warmupphrase.update(where={"id": phrase_id}, data=data)


async def delete_phrase(phrase_id: str):
    return await db.warmupphrase.delete(where={"id": phrase_id})


async def count_phrases() -> int:
    return await db.warmupphrase.count()


async def seed_default_phrases() -> int:
    """Popula o banco de frases com um conjunto inicial, apenas se a tabela
    estiver vazia (chamado automaticamente na subida da API)."""
    existing = await count_phrases()
    if existing > 0:
        return 0

    defaults = [
        ("{Oi|Olá|E aí|Opa}, {tudo bem|tudo certo|beleza}?", "saudacao"),
        ("{Bom dia|Boa tarde|Boa noite}! {Como você está?|Tudo tranquilo por aí?}", "saudacao"),
        ("{Vi que|Notei que} você {mandou mensagem|chamou} {mais cedo|agora há pouco}, {tudo certo?|precisa de algo?}", "geral"),
        ("{Só passando pra dizer oi|Só dando um alô|Mensagem rápida}: {como estão as coisas?|tudo em ordem?}", "geral"),
        ("{Combinamos aquilo mesmo|Ficou certo então}, {qualquer coisa me avisa|me chama se precisar}.", "confirmacao"),
        ("{Beleza|Show|Perfeito}, {obrigado|valeu}!", "confirmacao"),
        ("{Ok|Certo|Entendido}, {vou verificar|vou dar uma olhada} e {te retorno|falo com você} {daqui a pouco|em breve}.", "confirmacao"),
        ("{Tudo certo por aqui|Por aqui tudo tranquilo}, {e por aí?|e com você?}", "geral"),
        ("{Depois te conto|Te aviso mais tarde} {como ficou|como foi}, {combinado?|fechado?}", "geral"),
        ("{Falou|Beleza|Tranquilo}, {até mais|até logo|nos falamos}!", "despedida"),
        ("{Valeu pela paciência|Obrigado por esperar}, {já resolvi|já ajeitei} {aqui|por aqui}.", "confirmacao"),
        ("{Oi, tudo bem|E aí, tudo certo}? {Faz tempo que não conversamos|Há quanto tempo}!", "saudacao"),
    ]
    for text, category in defaults:
        await create_phrase(text, category)
    return len(defaults)
