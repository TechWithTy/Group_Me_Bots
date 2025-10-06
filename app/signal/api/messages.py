"""Message delivery endpoints backed by the in-memory Signal state."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Body, HTTPException, Path, Query, Response, status
from pydantic import BaseModel, Field

from .helpers import ensure_account, now_ms, state

router = APIRouter()
router_v2 = APIRouter()


class SendMessageV1(BaseModel):
    message: str
    number: str
    recipients: List[str] = Field(default_factory=list)
    is_group: Optional[bool] = False
    base64_attachment: Optional[str] = None


class LinkPreviewType(BaseModel):
    url: str
    title: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class MessageMention(BaseModel):
    start: int
    length: int
    uuid: str


class SendMessageV2(BaseModel):
    message: str
    number: str
    recipients: List[str] = Field(default_factory=list)
    text_mode: Optional[str] = "normal"
    base64_attachments: Optional[List[str]] = None
    sticker: Optional[str] = None
    edit_timestamp: Optional[int] = None
    quote_timestamp: Optional[int] = None
    quote_author: Optional[str] = None
    quote_message: Optional[str] = None
    quote_mentions: Optional[List[MessageMention]] = None
    mentions: Optional[List[MessageMention]] = None
    link_preview: Optional[LinkPreviewType] = None
    view_once: Optional[bool] = False
    notify_self: Optional[bool] = True


class RemoteDeleteRequest(BaseModel):
    recipient: str
    timestamp: int


class TypingIndicatorRequest(BaseModel):
    recipient: str


class SendMessageResponse(BaseModel):
    timestamp: str


class RemoteDeleteResponse(BaseModel):
    timestamp: str


def _store_attachments(contents: Optional[List[str]]) -> List[str]:
    if not contents:
        return []
    return [state.store_attachment(content, "application/octet-stream") for content in contents]


def _deliver_message(
    sender: str,
    recipients: List[str],
    message: str,
    attachments: List[str],
    view_once: bool,
    sticker: Optional[str],
) -> int:
    if not recipients:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one recipient is required")
    timestamp = now_ms()
    payload = {
        "timestamp": timestamp,
        "sender": sender,
        "message": message,
        "attachments": attachments,
        "view_once": view_once,
        "sticker": sticker,
        "recipients": recipients,
    }
    ensure_account(sender)
    for recipient in recipients:
        account = ensure_account(recipient)
        account.inbox.append(payload.copy())
    return timestamp


def _receive(account_number: str, limit: Optional[int]) -> List[dict]:
    account = ensure_account(account_number)
    messages = account.inbox
    if limit is not None:
        selected = messages[:limit]
        del messages[:limit]
    else:
        selected = list(messages)
        account.inbox.clear()
    return selected


def _remove_message(account_number: str, timestamp: int) -> bool:
    account = ensure_account(account_number)
    before = len(account.inbox)
    account.inbox = [msg for msg in account.inbox if msg["timestamp"] != timestamp]
    return len(account.inbox) != before


@router.post("/send")
async def send_message_v1(data: SendMessageV1 = Body(..., description="Input Data")) -> dict:
    attachments = _store_attachments([data.base64_attachment] if data.base64_attachment else [])
    timestamp = _deliver_message(data.number, data.recipients, data.message, attachments, False, None)
    return {"message": "Message sent", "timestamp": str(timestamp)}


@router_v2.post("/send", response_model=SendMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_message_v2(data: SendMessageV2 = Body(..., description="Input Data")) -> SendMessageResponse:
    attachments = _store_attachments(data.base64_attachments)
    timestamp = _deliver_message(data.number, data.recipients, data.message, attachments, data.view_once or False, data.sticker)
    return SendMessageResponse(timestamp=str(timestamp))


@router.get("/receive/{number}")
async def receive_messages(
    number: str = Path(..., description="Registered Phone Number"),
    timeout: Optional[str] = Query("1", description="Receive timeout in seconds"),
    ignore_attachments: Optional[str] = Query(None, description="Ignore message attachments"),
    ignore_stories: Optional[str] = Query(None, description="Ignore stories"),
    max_messages: Optional[str] = Query(None, description="Maximum messages to receive"),
    send_read_receipts: Optional[str] = Query(None, description="Send read receipts"),
) -> List[dict]:
    limit = int(max_messages) if max_messages else None
    messages = _receive(number, limit)
    response_messages = []
    for stored in messages:
        payload = stored.copy()
        if ignore_attachments:
            payload["attachments"] = []
        response_messages.append(payload)
    return response_messages


@router.put("/typing-indicator/{number}", status_code=status.HTTP_204_NO_CONTENT)
async def show_typing_indicator(
    number: str = Path(..., description="Registered Phone Number"),
    data: TypingIndicatorRequest = Body(..., description="Type"),
) -> Response:
    account = ensure_account(number)
    account.typing.add(data.recipient)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/typing-indicator/{number}", status_code=status.HTTP_204_NO_CONTENT)
async def hide_typing_indicator(
    number: str = Path(..., description="Registered Phone Number"),
    data: TypingIndicatorRequest = Body(..., description="Type"),
) -> Response:
    account = ensure_account(number)
    account.typing.discard(data.recipient)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/remote-delete/{number}", status_code=status.HTTP_201_CREATED, response_model=RemoteDeleteResponse)
async def remote_delete_message(
    number: str = Path(..., description="Registered Phone Number"),
    data: RemoteDeleteRequest = Body(..., description="Type"),
) -> RemoteDeleteResponse:
    _remove_message(data.recipient, data.timestamp)
    return RemoteDeleteResponse(timestamp=str(now_ms()))


__all__ = ["router", "router_v2"]

