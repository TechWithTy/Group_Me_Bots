from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class SponsoredContent(BaseModel):
    """Tracks sponsored messages and native advertising campaigns."""
    id: str = Field(..., description="Unique ID for sponsored content")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")
    monetization_source_id: str = Field(..., description="Linked monetization source")

    campaign_name: str = Field(..., description="Name of the advertising campaign")
    advertiser: str = Field(..., description="Company or entity sponsoring the content")
    content_type: str = Field(..., description="Type of content (message, recommendation, tie-in)")

    # Targeting and delivery
    target_groups: List[str] = Field(default_factory=list, description="Groups where content is delivered")
    trigger_keywords: List[str] = Field(default_factory=list, description="Keywords that trigger native ads")

    # Performance metrics
    impressions: int = Field(default=0, description="Number of times content was shown")
    clicks: int = Field(default=0, description="Number of user interactions")
    conversions: int = Field(default=0, description="Successful monetization events")

    is_active: bool = Field(default=True, description="Whether the campaign is running")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class DataMonetization(BaseModel):
    """Tracks data collection and sales for market research."""
    id: str = Field(..., description="Unique ID for data monetization event")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")
    monetization_source_id: str = Field(..., description="Linked monetization source")

    data_type: str = Field(..., description="Type of data collected (behavior, sentiment, surveys)")
    anonymization_level: str = Field(..., description="How data is anonymized")
    buyer_company: str = Field(..., description="Company purchasing the data")

    # Survey details (if applicable)
    survey_questions: Optional[List[str]] = None
    response_count: int = Field(default=0, description="Number of responses collected")

    revenue_generated: float = Field(..., description="Revenue from this data sale")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class B2BService(BaseModel):
    """Tracks B2B services like lead generation and consulting."""
    id: str = Field(..., description="Unique ID for B2B service")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")
    monetization_source_id: str = Field(..., description="Linked monetization source")

    service_type: str = Field(..., description="Type of service (lead_generation, consulting, baas)")
    client_company: str = Field(..., description="Company receiving the service")

    # Service details
    leads_generated: int = Field(default=0, description="Number of leads generated")
    service_delivered: bool = Field(default=False, description="Whether service was completed")

    contract_value: float = Field(..., description="Value of the service contract")
    recurring: bool = Field(default=False, description="Whether it's a recurring service")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True
