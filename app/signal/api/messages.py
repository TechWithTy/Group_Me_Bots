"""
Signal Messages API Routes

This module handles all message-related operations including:
- Message sending (v1 and v2)
- Message receiving
- Message reactions
- Read receipts
- Typing indicators
- Remote message deletion
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Path, Body, Query
from pydantic import BaseModel

router = APIRouter()


# Pydantic models for request/response bodies
class SendMessageV1(BaseModel):
    message: str
    number: str
    recipients: List[str] = []
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
    recipients: List[str] = []
    text_mode: Optional[str] = "normal"  # "normal" or "styled"
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


class Reaction(BaseModel):
    reaction: str
    recipient: str
    target_author: str
    timestamp: int


class Receipt(BaseModel):
    receipt_type: str  # "read" or "viewed"
    recipient: str
    timestamp: int


class RemoteDeleteRequest(BaseModel):
    recipient: str
    timestamp: int


class TypingIndicatorRequest(BaseModel):
    recipient: str


class SendMessageResponse(BaseModel):
    timestamp: str


class SendMessageError(BaseModel):
    error: str
    account: Optional[str] = None
    challenge_tokens: Optional[List[str]] = None


class RemoteDeleteResponse(BaseModel):
    timestamp: str


class ErrorResponse(BaseModel):
    error: str


@router.post("/send")
async def send_message_v1(
    data: SendMessageV1 = Body(..., description="Input Data")
):
    """
    Send a signal message (deprecated v1 endpoint).

    This is the deprecated v1 message sending endpoint.
    Use /v2/send for new implementations.
    """
    # TODO: Implement v1 message sending logic
    return {"message": "Message sent", "timestamp": "1234567890"}


@router.post("/v2/send")
async def send_message_v2(
    data: SendMessageV2 = Body(..., description="Input Data")
):
    """
    Send a signal message.

    Send a message using the improved v2 API with support for styling,
    mentions, quotes, and other advanced features.
    """
    # TODO: Implement v2 message sending logic
    return SendMessageResponse(timestamp="1234567890")


@router.get("/receive/{number}")
async def receive_messages(
    number: str = Path(..., description="Registered Phone Number"),
    timeout: Optional[str] = Query("1", description="Receive timeout in seconds"),
    ignore_attachments: Optional[str] = Query(None, description="Ignore message attachments"),
    ignore_stories: Optional[str] = Query(None, description="Ignore stories"),
    max_messages: Optional[str] = Query(None, description="Maximum messages to receive"),
    send_read_receipts: Optional[str] = Query(None, description="Send read receipts")
):
    """
    Receive Signal Messages from the Signal Network.

    Receives pending messages from the Signal network.
    """
    # TODO: Implement message receiving logic
    return []  # Placeholder response


@router.post("/reactions/{number}")
async def send_reaction(
    number: str = Path(..., description="Registered phone number"),
    data: Reaction = Body(..., description="Reaction")
):
    """
    Send a reaction.

    React to a message with an emoji or other reaction.
    """
    # TODO: Implement reaction sending logic
    return {"message": "Reaction sent successfully"}


@router.delete("/reactions/{number}")
async def remove_reaction(
    number: str = Path(..., description="Registered phone number"),
    data: Reaction = Body(..., description="Reaction")
):
    """
    Remove a reaction.

    Remove a previously sent reaction from a message.
    """
    # TODO: Implement reaction removal logic
    return {"message": "Reaction removed successfully"}


@router.post("/receipts/{number}")
async def send_receipt(
    number: str = Path(..., description="Registered phone number"),
    data: Receipt = Body(..., description="Receipt")
):
    """
    Send a receipt.

    Send a read or viewed receipt for a message.
    """
    # TODO: Implement receipt sending logic
    return {"message": "Receipt sent successfully"}


@router.put("/typing-indicator/{number}")
async def show_typing_indicator(
    number: str = Path(..., description="Registered Phone Number"),
    data: TypingIndicatorRequest = Body(..., description="Type")
):
    """
    Show Typing Indicator.

    Shows that the user is currently typing a message.
    """
    # TODO: Implement typing indicator logic
    return {"message": "Typing indicator shown"}


@router.delete("/typing-indicator/{number}")
async def hide_typing_indicator(
    number: str = Path(..., description="Registered Phone Number"),
    data: TypingIndicatorRequest = Body(..., description="Type")
):
    """
    Hide Typing Indicator.

    Hides the typing indicator when the user stops typing.
    """
    # TODO: Implement typing indicator hiding logic
    return {"message": "Typing indicator hidden"}


@router.delete("/remote-delete/{number}")
async def remote_delete_message(
    number: str = Path(..., description="Registered Phone Number"),
    data: RemoteDeleteRequest = Body(..., description="Type")
):
    """
    Delete a signal message.

    Remotely delete a message that was previously sent.
    """
    # TODO: Implement remote message deletion logic
    return RemoteDeleteResponse(timestamp="1234567890")
