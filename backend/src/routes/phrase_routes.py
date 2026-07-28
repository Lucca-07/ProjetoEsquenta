from fastapi import APIRouter

from src.controllers import phrase_controller
from src.models.phrase_schema import PhraseCreate, PhraseUpdate, PhraseResponse

router = APIRouter(prefix="/phrases", tags=["phrases"])


@router.get("", response_model=list[PhraseResponse])
async def list_phrases(active_only: bool = False, category: str | None = None):
    return await phrase_controller.list_phrases(active_only=active_only, category=category)


@router.post("", response_model=PhraseResponse, status_code=201)
async def create_phrase(payload: PhraseCreate):
    return await phrase_controller.create_phrase(payload.text, payload.category)


@router.put("/{phrase_id}", response_model=PhraseResponse)
async def update_phrase(phrase_id: str, payload: PhraseUpdate):
    return await phrase_controller.update_phrase(
        phrase_id, payload.text, payload.category, payload.active
    )


@router.delete("/{phrase_id}")
async def delete_phrase(phrase_id: str):
    return await phrase_controller.delete_phrase(phrase_id)
