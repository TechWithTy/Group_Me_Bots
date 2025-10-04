from __future__ import annotations
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Merchant(BaseModel):
    """A merchant providing products, scoped to a tenant."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant this merchant belongs to")
    name: str
    backend_url: Optional[str] = Field(None, description="API endpoint for the merchant's backend for ACP")
    config: Dict[str, Any] = Field(default_factory=dict, description="ACP settings, API keys, etc.")

class Product(BaseModel):
    """A product offered by a merchant."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    merchant_id: uuid.UUID = Field(..., description="Foreign key to the Merchant")
    sku: str = Field(..., index=True)
    name: str
    description: Optional[str] = None
    price_cents: int
    currency: str = "USD"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GroupOrder(BaseModel):
    """An order initiated within a group."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    group_id: uuid.UUID = Field(..., description="The group where the order was placed")
    initiator_user_id: uuid.UUID = Field(..., description="The user who started the order")
    merchant_id: uuid.UUID
    status: str = Field("pending", description="e.g., 'pending', 'confirmed', 'shipped', 'cancelled'")
    total_cents: int
    currency: str = "USD"

    created_at: datetime = Field(default_factory=datetime.utcnow)

class OrderLineItem(BaseModel):
    """A single item within a group order, linked to a specific user."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    group_order_id: uuid.UUID
    user_id: uuid.UUID
    product_id: uuid.UUID
    quantity: int
    price_cents: int
