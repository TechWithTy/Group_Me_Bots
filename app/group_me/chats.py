"""
GroupMe API Chats and Bots endpoints implementation.

This module implements the GroupMe API endpoints for:
- Direct message chats (GET /chats)
- Message likes (POST /messages/:conversation_id/:message_id/like|unlike)
- Bot management (POST /bots, GET /bots, POST /bots/post, POST /bots/destroy)

All endpoints follow the official GroupMe API specification.
"""
from __future__ import annotations

import asyncio
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends, Path
from pydantic import BaseModel, Field

from app.dependencies import get_groupme_client, get_tenant_from_api_key

logger = logging.getLogger(__name__)

# Initialize router
router = APIRouter(prefix="/api/v1", tags=["groupme"])

# Pydantic Models for API responses
class ChatMessage(BaseModel):
    """Model for chat message data."""
    attachments: List[Dict[str, Any]] = Field(default_factory=list)
    avatar_url: Optional[str] = None
    conversation_id: str
    created_at: int  # Unix timestamp
    favorited_by: List[str] = Field(default_factory=list)
    id: str
    name: Optional[str] = None
    recipient_id: str
    sender_id: str
    sender_type: str
    source_guid: str
    text: str
    user_id: str

class ChatData(BaseModel):
    """Model for chat data."""
    created_at: int  # Unix timestamp
    updated_at: int  # Unix timestamp
    last_message: ChatMessage
    messages_count: int
    other_user: Dict[str, Any]

class BotData(BaseModel):
    """Model for bot data."""
    bot_id: str
    group_id: str
    name: str
    avatar_url: Optional[str] = None
    callback_url: Optional[str] = None
    dm_notification: bool = False
    active: bool = True

# Chats Endpoints

@router.get("/chats", response_model=List[ChatData])
async def get_chats(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(20, ge=1, le=100, description="Number of chats per page"),
    groupme_client = Depends(get_groupme_client),
    tenant = Depends(get_tenant_from_api_key)
):
    """
    Returns a paginated list of direct message chats.

    - **page**: Page number (starts at 1)
    - **per_page**: Number of chats per page (1-100)
    """
    try:
        # In a real implementation, this would call the GroupMe API
        # For now, return mock data structure
        chats = await _get_mock_chats(page, per_page)

        logger.info(f"Retrieved {len(chats)} chats for tenant {tenant.id}, page {page}")
        return chats

    except Exception as e:
        logger.error(f"Error retrieving chats for tenant {tenant.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve chats")

# Message Like/Unlike Endpoints

@router.post("/messages/{conversation_id}/{message_id}/like")
async def like_message(
    conversation_id: str = Path(..., description="Conversation ID"),
    message_id: str = Path(..., description="Message ID"),
    groupme_client = Depends(get_groupme_client),
    tenant = Depends(get_tenant_from_api_key)
):
    """
    Like a message in a conversation.

    - **conversation_id**: The conversation containing the message
    - **message_id**: The message to like
    """
    try:
        # In a real implementation, this would call GroupMe API
        # For now, simulate successful like operation
        await _mock_like_message(conversation_id, message_id, tenant.id)

        logger.info(f"User liked message {message_id} in conversation {conversation_id} for tenant {tenant.id}")
        return {"status": "success", "message": "Message liked"}

    except Exception as e:
        logger.error(f"Error liking message for tenant {tenant.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to like message")

@router.post("/messages/{conversation_id}/{message_id}/unlike")
async def unlike_message(
    conversation_id: str = Path(..., description="Conversation ID"),
    message_id: str = Path(..., description="Message ID"),
    groupme_client = Depends(get_groupme_client),
    tenant = Depends(get_tenant_from_api_key)
):
    """
    Unlike a message in a conversation.

    - **conversation_id**: The conversation containing the message
    - **message_id**: The message to unlike
    """
    try:
        # In a real implementation, this would call GroupMe API
        # For now, simulate successful unlike operation
        await _mock_unlike_message(conversation_id, message_id, tenant.id)

        logger.info(f"User unliked message {message_id} in conversation {conversation_id} for tenant {tenant.id}")
        return {"status": "success", "message": "Message unliked"}

    except Exception as e:
        logger.error(f"Error unliking message for tenant {tenant.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to unlike message")

# Bots Endpoints

@router.post("/bots", response_model=BotData)
async def create_bot(
    name: str = Query(..., description="Bot name"),
    group_id: str = Query(..., description="Group ID"),
    avatar_url: Optional[str] = Query(None, description="Bot avatar URL"),
    callback_url: Optional[str] = Query(None, description="Bot callback URL"),
    dm_notification: bool = Query(False, description="DM notification setting"),
    active: bool = Query(True, description="Bot active status"),
    groupme_client = Depends(get_groupme_client),
    tenant = Depends(get_tenant_from_api_key)
):
    """
    Create a new bot.

    - **name**: Bot name (required)
    - **group_id**: Group ID (required)
    - **avatar_url**: Bot avatar URL (optional)
    - **callback_url**: Bot callback URL (optional)
    - **dm_notification**: DM notification setting (optional)
    - **active**: Bot active status (optional)
    """
    try:
        # In a real implementation, this would call GroupMe API
        # For now, return mock bot data
        bot_data = await _mock_create_bot(
            name, group_id, avatar_url, callback_url, dm_notification, active, tenant.id
        )

        logger.info(f"Created bot '{name}' for tenant {tenant.id} in group {group_id}")
        return BotData(**bot_data)

    except Exception as e:
        logger.error(f"Error creating bot for tenant {tenant.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create bot")

@router.get("/bots", response_model=List[BotData])
async def list_bots(
    groupme_client = Depends(get_groupme_client),
    tenant = Depends(get_tenant_from_api_key)
):
    """
    List bots created by the authenticated user.
    """
    try:
        # In a real implementation, this would call GroupMe API
        # For now, return mock bot data
        bots = await _mock_list_bots(tenant.id)

        logger.info(f"Retrieved {len(bots)} bots for tenant {tenant.id}")
        return [BotData(**bot) for bot in bots]

    except Exception as e:
        logger.error(f"Error listing bots for tenant {tenant.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to list bots")

@router.post("/bots/post")
async def post_bot_message(
    bot_id: str = Query(..., description="Bot ID"),
    text: str = Query(..., description="Message text"),
    picture_url: Optional[str] = Query(None, description="Picture URL"),
    groupme_client = Depends(get_groupme_client),
    tenant = Depends(get_tenant_from_api_key)
):
    """
    Post a message from a bot.

    - **bot_id**: Bot ID (required)
    - **text**: Message text (required)
    - **picture_url**: Picture URL (optional)
    """
    try:
        # In a real implementation, this would call GroupMe API
        # For now, simulate successful message posting
        await _mock_post_bot_message(bot_id, text, picture_url, tenant.id)

        logger.info(f"Posted message from bot {bot_id} for tenant {tenant.id}")
        return {"status": "success", "message": "Bot message posted"}

    except Exception as e:
        logger.error(f"Error posting bot message for tenant {tenant.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to post bot message")

@router.post("/bots/destroy")
async def destroy_bot(
    bot_id: str = Query(..., description="Bot ID"),
    groupme_client = Depends(get_groupme_client),
    tenant = Depends(get_tenant_from_api_key)
):
    """
    Remove a bot.

    - **bot_id**: Bot ID to destroy (required)
    """
    try:
        # In a real implementation, this would call GroupMe API
        # For now, simulate successful bot destruction
        await _mock_destroy_bot(bot_id, tenant.id)

        logger.info(f"Destroyed bot {bot_id} for tenant {tenant.id}")
        return {"status": "success", "message": "Bot destroyed"}

    except Exception as e:
        logger.error(f"Error destroying bot for tenant {tenant.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to destroy bot")

# Mock implementations (replace with actual GroupMe API calls)

async def _get_mock_chats(page: int, per_page: int) -> List[Dict[str, Any]]:
    """Mock implementation of GET /chats."""
    # Generate mock chat data
    chats = []
    start_index = (page - 1) * per_page

    for i in range(start_index, min(start_index + per_page, 50)):  # Max 50 mock chats
        chat = {
            "created_at": int(datetime.utcnow().timestamp()) - (i * 3600),
            "updated_at": int(datetime.utcnow().timestamp()) - (i * 1800),
            "last_message": {
                "attachments": [],
                "avatar_url": "https://i.groupme.com/200x200.jpeg.abcdef",
                "conversation_id": f"12345+67890_{i}",
                "created_at": int(datetime.utcnow().timestamp()) - (i * 1800),
                "favorited_by": [],
                "id": f"1234567890_{i}",
                "name": f"User {i}",
                "recipient_id": f"67890_{i}",
                "sender_id": f"12345_{i}",
                "sender_type": "user",
                "source_guid": f"GUID_{i}",
                "text": f"Hello world message {i}",
                "user_id": f"12345_{i}"
            },
            "messages_count": 10 + i,
            "other_user": {
                "avatar_url": "https://i.groupme.com/200x200.jpeg.abcdef",
                "id": 12345 + i,
                "name": f"User {i}"
            }
        }
        chats.append(chat)

    return chats

async def _mock_like_message(conversation_id: str, message_id: str, tenant_id: str) -> None:
    """Mock implementation of POST /messages/:conversation_id/:message_id/like."""
    # In production, call actual GroupMe API
    await asyncio.sleep(0.1)  # Simulate API call delay
    logger.debug(f"Mock liked message {message_id} in conversation {conversation_id} for tenant {tenant_id}")

async def _mock_unlike_message(conversation_id: str, message_id: str, tenant_id: str) -> None:
    """Mock implementation of POST /messages/:conversation_id/:message_id/unlike."""
    # In production, call actual GroupMe API
    await asyncio.sleep(0.1)  # Simulate API call delay
    logger.debug(f"Mock unliked message {message_id} in conversation {conversation_id} for tenant {tenant_id}")

async def _mock_create_bot(name: str, group_id: str, avatar_url: str, callback_url: str, dm_notification: bool, active: bool, tenant_id: str) -> Dict[str, Any]:
    """Mock implementation of POST /bots."""
    # In production, call actual GroupMe API
    await asyncio.sleep(0.1)  # Simulate API call delay

    return {
        "bot_id": f"bot_{int(datetime.utcnow().timestamp())}_{hash(name) % 10000}",
        "group_id": group_id,
        "name": name,
        "avatar_url": avatar_url,
        "callback_url": callback_url,
        "dm_notification": dm_notification,
        "active": active
    }

async def _mock_list_bots(tenant_id: str) -> List[Dict[str, Any]]:
    """Mock implementation of GET /bots."""
    # In production, call actual GroupMe API
    await asyncio.sleep(0.1)  # Simulate API call delay

    return [
        {
            "bot_id": "bot_1234567890",
            "group_id": "group_1234567890",
            "name": "Test Bot 1",
            "avatar_url": "https://i.groupme.com/123456789",
            "callback_url": "https://example.com/bots/callback",
            "dm_notification": False,
            "active": True
        },
        {
            "bot_id": "bot_0987654321",
            "group_id": "group_0987654321",
            "name": "Test Bot 2",
            "avatar_url": "https://i.groupme.com/098765432",
            "callback_url": None,
            "dm_notification": True,
            "active": True
        }
    ]

async def _mock_post_bot_message(bot_id: str, text: str, picture_url: str, tenant_id: str) -> None:
    """Mock implementation of POST /bots/post."""
    # In production, call actual GroupMe API
    await asyncio.sleep(0.1)  # Simulate API call delay
    logger.debug(f"Mock posted message from bot {bot_id} for tenant {tenant_id}: {text[:50]}...")

async def _mock_destroy_bot(bot_id: str, tenant_id: str) -> None:
    """Mock implementation of POST /bots/destroy."""
    # In production, call actual GroupMe API
    await asyncio.sleep(0.1)  # Simulate API call delay
    logger.debug(f"Mock destroyed bot {bot_id} for tenant {tenant_id}")

# Export router for inclusion in main app
__all__ = ["router"]