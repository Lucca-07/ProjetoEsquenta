import random

from src.repositories import number_repository, warmup_log_repository


async def get_partner_for(number) -> object | None:
    """Escolhe um parceiro de conversa para o número dado, dentre os números
    ativos, priorizando pares já existentes (para manter conversas coerentes)
    e, na ausência deles, sorteando outro número ativo diferente do próprio."""

    active_numbers = await number_repository.list_all(active_only=True)
    candidates = [n for n in active_numbers if n.id != number.id]
    if not candidates:
        return None

    pairs = await warmup_log_repository.list_active_pairs()
    existing_partner_ids = {
        p.numberBId if p.numberAId == number.id else p.numberAId
        for p in pairs
        if p.numberAId == number.id or p.numberBId == number.id
    }
    existing_candidates = [c for c in candidates if c.id in existing_partner_ids]

    if existing_candidates and random.random() < 0.7:
        # 70% de chance de continuar uma conversa com um parceiro já pareado
        return random.choice(existing_candidates)

    return random.choice(candidates)


async def ensure_pair(number_a_id: str, number_b_id: str):
    return await warmup_log_repository.get_or_create_pair(number_a_id, number_b_id)
