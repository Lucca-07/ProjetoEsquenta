from fastapi import HTTPException

from src.repositories import phrase_repository


async def list_phrases(active_only: bool = False, category: str | None = None):
    return await phrase_repository.list_phrases(active_only=active_only, category=category)


async def create_phrase(text: str, category: str):
    return await phrase_repository.create_phrase(text, category)


async def update_phrase(phrase_id: str, text: str | None, category: str | None, active: bool | None):
    phrase = await phrase_repository.get_phrase(phrase_id)
    if phrase is None:
        raise HTTPException(status_code=404, detail="Frase não encontrada")
    return await phrase_repository.update_phrase(phrase_id, text=text, category=category, active=active)


async def delete_phrase(phrase_id: str):
    phrase = await phrase_repository.get_phrase(phrase_id)
    if phrase is None:
        raise HTTPException(status_code=404, detail="Frase não encontrada")
    await phrase_repository.delete_phrase(phrase_id)
    return {"deleted": True}
