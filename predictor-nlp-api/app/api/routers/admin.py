from fastapi import APIRouter
from app.domain.dtos import CacheBustRequest
from app.infrastructure.cache import clear_all, clear_keys

router = APIRouter(prefix="/admin", tags=["admin"])

@router.post("/cache/bust")
def cache_bust(req: CacheBustRequest):
    if not req.subjectId and not req.channel:
        clear_all()
        return {"cleared": "all"}
    keys = []
    if req.channel:
        keys.append(("channel", req.channel, "*"))  # limpar todas versões: wildcard-like
    if req.subjectId:
        keys.append(("subject", req.subjectId, "*"))

    # TTLCache não suporta wildcard → varremos manualmente
    from app.infrastructure.cache import model_cache
    to_del = []
    for k in list(model_cache.keys()):
        if req.channel and k[0] == "channel" and k[1] == req.channel:
            to_del.append(k)
        if req.subjectId and k[0] == "subject" and k[1] == req.subjectId:
            to_del.append(k)
    clear_keys(to_del)
    return {"cleared_keys": [list(k) for k in to_del]}
