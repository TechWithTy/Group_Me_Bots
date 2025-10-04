from __future__ import annotations

import uuid
from datetime import datetime
from typing import Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class MonetizationSourceType(str, Enum):
    AFFILIATE_LINK = "affiliate_link"
    PAID_SUBSCRIPTION = "paid_subscription"
    PREMIUM_FEATURE = "premium_feature"
    AD_IMPRESSION = "ad_impression"
    DATA_SALE = "data_sale"
    # New monetization strategies
    SPONSORED_CONTENT = "sponsored_content"
    NATIVE_ADVERTISING = "native_advertising"
    PROMOTIONAL_TIE_IN = "promotional_tie_in"
    MARKET_RESEARCH = "market_research"
    CUSTOM_SURVEYS = "custom_surveys"
    LEAD_GENERATION = "lead_generation"
    BOTS_AS_A_SERVICE = "bots_as_a_service"
    CONSULTING_SERVICE = "consulting_service"
    PAY_PER_USE = "pay_per_use"
    TRANSACTION_FEE = "transaction_fee"
    COMMUNITY_SUPPORT = "community_support"

class RevenueModel(str, Enum):
    PAY_PER_CLICK = "pay_per_click"
    RECURRING = "recurring"
    ONE_TIME_FEE = "one_time_fee"

class MonetizationSource(BaseModel):
    """Defines monetization strategies and tracks revenue sources."""
    id: str = Field(..., description="Unique ID for the monetization source")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")

    source_type: MonetizationSourceType = Field(..., description="Type of monetization")
    source_name: str = Field(..., description="Human-readable name for the source")
    revenue_model: RevenueModel = Field(..., description="How revenue is generated")

    details: Dict[str, Any] = Field(default_factory=dict, description="Additional configuration or metadata")

    is_active: bool = Field(default=True, description="Whether this source is currently active")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
