"""Endpoints for sending and removing message reactions."""

from __future__ import annotations

from fastapi import APIRouter, Body, Path, Response, status
from pydantic import BaseModel

from .helpers import ensure_account


router = APIRouter()


class ReactionRequest(BaseModel):
    reaction: str
    recipient: str
    target_author: str
    timestamp: int


@router.post("/{number}", status_code=status.HTTP_204_NO_CONTENT)
async def send_reaction(
    number: str = Path(..., description="Registered phone number"),
    data: ReactionRequest = Body(..., description="Reaction"),
) -> Response:
    """Record that ``number`` reacted to a message."""

    account = ensure_account(number)
    ensure_account(data.recipient)
    key = (data.recipient, data.target_author, data.timestamp)
    account.reactions[key] = data.reaction
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{number}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_reaction(
    number: str = Path(..., description="Registered phone number"),
    data: ReactionRequest = Body(..., description="Reaction"),
) -> Response:
    """Remove a previously recorded reaction."""

    account = ensure_account(number)
    key = (data.recipient, data.target_author, data.timestamp)
    account.reactions.pop(key, None)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
