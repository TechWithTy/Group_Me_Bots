"""Sticker pack endpoints backed by the in-memory store."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Body, HTTPException, Path, Response, status
from pydantic import BaseModel

from .helpers import ensure_account
from .state.models import StickerPack

router = APIRouter()


class AddStickerPackRequest(BaseModel):
    pack_id: str
    pack_key: str


class ListInstalledStickerPacksResponse(BaseModel):
    id: str
    key: str
    title: str
    author: str


@router.get("/{number}", response_model=list[ListInstalledStickerPacksResponse])
async def list_sticker_packs(number: str = Path(..., description="Registered Phone Number")) -> list[ListInstalledStickerPacksResponse]:
    account = ensure_account(number)
    return [
        ListInstalledStickerPacksResponse(id=pack.pack_id, key=pack.pack_key, title=pack.title, author=pack.author)
        for pack in account.sticker_packs.values()
    ]


@router.post("/{number}", status_code=status.HTTP_204_NO_CONTENT)
async def add_sticker_pack(
    number: str = Path(..., description="Registered Phone Number"),
    data: AddStickerPackRequest = Body(..., description="Request"),
) -> Response:
    if not data.pack_id or not data.pack_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Both pack_id and pack_key are required")
    account = ensure_account(number)
    account.sticker_packs[data.pack_id] = StickerPack(
        pack_id=data.pack_id,
        pack_key=data.pack_key,
        title=f"Sticker Pack {data.pack_id}",
        author="Signal CLI",
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
