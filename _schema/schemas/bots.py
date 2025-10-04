from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel, Field

class ChatBot(BaseModel):
    """Defines an AI bot and its capabilities."""
    id: str = Field(..., description="Unique ID for the bot")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")

    bot_name: str = Field(..., description="Human-readable name for the bot")
    bot_model: str = Field(..., description="Underlying AI model (e.g., GPT-4o, Llama 3)")
    function: str = Field(..., description="Bot's primary role (e.g., customer_support, affiliate_marketing, moderation)")

    monetization_source_id: str = Field(..., description="Primary monetization strategy for this bot")

    # Capabilities and settings
    capabilities: List[str] = Field(default_factory=list, description="List of bot capabilities")
    settings: Dict[str, Any] = Field(default_factory=dict, description="Bot-specific settings and configurations")

    is_active: bool = Field(default=True, description="Whether the bot is currently active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
