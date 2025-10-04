from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
from pydantic import BaseModel, Field

class AIUsage(BaseModel):
    """Tracks individual AI usage events."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Primary key for AI usage record")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")
    user_id: uuid.UUID = Field(..., description="Foreign key to the User who made the request")
    group_id: Optional[uuid.UUID] = Field(None, description="Foreign key to the Group if applicable")

    # Usage Details
    api_endpoint: str = Field(..., description="The AI API endpoint called (e.g., 'moderation', 'summarization')")
    credits_used: int = Field(..., description="Number of AI credits consumed")
    request_tokens: Optional[int] = Field(None, description="Input tokens in the request")
    response_tokens: Optional[int] = Field(None, description="Output tokens in the response")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata about the usage")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class CommandUsage(BaseModel):
    """Tracks executions of custom commands."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Primary key for command usage record")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")
    group_id: uuid.UUID = Field(..., description="Foreign key to the Group")
    user_id: uuid.UUID = Field(..., description="Foreign key to the User who executed the command")
    custom_command_id: uuid.UUID = Field(..., description="Foreign key to the CustomCommand")

    # Execution Details
    trigger_text: str = Field(..., description="The text that triggered the command")
    execution_time_ms: Optional[int] = Field(None, description="Time taken to execute in milliseconds")
    success: bool = Field(default=True, description="Whether the command executed successfully")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional execution metadata")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class GroupDailyStats(BaseModel):
    """Daily aggregated statistics for a group."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Primary key for group daily stats")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")
    group_id: uuid.UUID = Field(..., description="Foreign key to the Group")

    # Date
    date: date = Field(..., description="The date these stats are for")

    # Activity Metrics
    total_messages: int = Field(default=0, description="Total messages sent in the group")
    unique_active_users: int = Field(default=0, description="Number of unique users active that day")
    new_users_joined: int = Field(default=0, description="Number of new users who joined")

    # AI Usage
    ai_credits_used: int = Field(default=0, description="Total AI credits used in the group")
    ai_requests_made: int = Field(default=0, description="Number of AI requests made")

    # Moderation
    infractions_recorded: int = Field(default=0, description="Number of moderation infractions")
    users_warned: int = Field(default=0, description="Number of users warned")
    users_kicked: int = Field(default=0, description="Number of users kicked")

    # Commands
    custom_commands_executed: int = Field(default=0, description="Number of custom commands executed")

    # Engagement
    average_session_duration_minutes: Optional[float] = Field(None, description="Average time users spent active")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional daily metadata")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class TenantMonthlyStats(BaseModel):
    """Monthly aggregated statistics for a tenant."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Primary key for tenant monthly stats")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")

    # Date
    year: int = Field(..., description="Year for these stats")
    month: int = Field(..., description="Month for these stats (1-12)")

    # Usage Metrics
    total_ai_credits_used: int = Field(default=0, description="Total AI credits used across all groups")
    total_groups_active: int = Field(default=0, description="Number of active groups")
    total_users_active: int = Field(default=0, description="Total unique active users")
    total_messages_processed: int = Field(default=0, description="Total messages processed")

    # Financial Metrics
    subscription_revenue_cents: int = Field(default=0, description="Revenue from subscriptions")
    additional_charges_cents: int = Field(default=0, description="Additional charges (e.g., overages)")

    # Performance Metrics
    average_response_time_ms: Optional[float] = Field(None, description="Average AI response time")
    uptime_percentage: Optional[float] = Field(None, description="System uptime percentage")

    # Growth Metrics
    new_groups_created: int = Field(default=0, description="New groups created this month")
    new_users_acquired: int = Field(default=0, description="New users acquired")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional monthly metadata")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class SystemHealth(BaseModel):
    """Tracks overall system health and performance metrics."""
    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Primary key for system health record")

    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # System Metrics
    total_active_tenants: int = Field(default=0, description="Number of active tenants")
    total_active_groups: int = Field(default=0, description="Total active groups across all tenants")
    total_active_users: int = Field(default=0, description="Total active users")

    # Performance Metrics
    average_api_latency_ms: Optional[float] = Field(None, description="Average API response latency")
    error_rate_percentage: float = Field(default=0.0, description="Percentage of requests with errors")

    # Resource Usage
    cpu_usage_percentage: Optional[float] = Field(None, description="Current CPU usage")
    memory_usage_percentage: Optional[float] = Field(None, description="Current memory usage")

    # Queue Metrics (if using message queues)
    pending_tasks: int = Field(default=0, description="Number of pending background tasks")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional system metadata")

    class Config:
        orm_mode = True

class BotInteraction(BaseModel):
    """Logs every interaction between a user and a bot."""
    id: str = Field(..., description="Unique ID for each interaction")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")

    timestamp: datetime = Field(..., description="When the interaction occurred")
    group_id: str = Field(..., description="Group where the interaction took place")
    member_id: str = Field(..., description="Member who initiated the interaction")
    bot_id: str = Field(..., description="Bot involved in the interaction")

    message_text: str = Field(..., description="Full text of the user's message")
    intent: str = Field(..., description="User's goal as interpreted by the bot")
    sentiment: str = Field(..., description="AI-analyzed sentiment score (positive, neutral, negative)")
    monetization_event: bool = Field(default=False, description="Whether this interaction led to a monetizable event")

    # Response details
    response_text: Optional[str] = None
    response_time_ms: Optional[int] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional interaction metadata")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class MonetizationEventLog(BaseModel):
    """Captures successful monetization events."""
    id: str = Field(..., description="Unique ID for the event log entry")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")

    interaction_id: str = Field(..., description="Interaction that triggered the event")
    monetization_source_id: str = Field(..., description="Monetization source used")

    revenue_generated: float = Field(..., description="Monetary value earned from this event")
    event_details: Dict[str, Any] = Field(default_factory=dict, description="Specific details like transaction ID, affiliate product ID, or ad ID")

    # Additional context
    group_id: Optional[str] = None
    member_id: Optional[str] = None
    bot_id: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class MetricCategory(str, Enum):
    CUSTOMER_EXPERIENCE = "customer_experience"
    OPERATIONAL_EFFICIENCY = "operational_efficiency"
    ENGAGEMENT_USAGE = "engagement_usage"
    PERFORMANCE = "performance"

class CustomerExperienceMetric(str, Enum):
    CSAT = "csat"  # Customer Satisfaction Score
    NPS = "nps"    # Net Promoter Score
    SENTIMENT_POSITIVE = "sentiment_positive"
    SENTIMENT_NEGATIVE = "sentiment_negative"
    SENTIMENT_NEUTRAL = "sentiment_neutral"
    BES = "bes"    # Bot Experience Score

class OperationalEfficiencyMetric(str, Enum):
    CONTAINMENT_RATE = "containment_rate"
    RESOLUTION_RATE = "resolution_rate"
    HUMAN_HANDOFF_RATE = "human_handoff_rate"
    FALLBACK_RATE = "fallback_rate"
    AVERAGE_HANDLING_TIME = "average_handling_time"
    COST_PER_CONVERSATION = "cost_per_conversation"
    ERROR_RATE = "error_rate"
    LATENCY = "latency"

class EngagementUsageMetric(str, Enum):
    ACTIVE_USERS = "active_users"
    RETENTION_RATE = "retention_rate"
    CONVERSATION_COMPLETION_RATE = "conversation_completion_rate"
    TOTAL_CONVERSATIONS = "total_conversations"
    BOUNCE_RATE = "bounce_rate"
    GOAL_COMPLETION_RATE = "goal_completion_rate"
    SESSION_DURATION = "session_duration"

class BotPerformanceMetrics(BaseModel):
    """Enhanced bot performance metrics with comprehensive KPI tracking."""
    id: str = Field(..., description="Unique ID for the metric entry")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")

    timestamp: datetime = Field(..., description="When the metric was recorded")
    bot_id: str = Field(..., description="Bot being measured")
    group_id: Optional[str] = Field(None, description="Group associated with the metric, if applicable")

    # Metric categorization
    metric_category: MetricCategory = Field(..., description="Category of the metric")
    metric_type: str = Field(..., description="Specific type of metric")

    # Core metric values
    metric_value: float = Field(..., description="Numerical value of the metric")
    metric_unit: str = Field(default="percentage", description="Unit of measurement (percentage, count, seconds, currency)")

    # Aggregation context
    aggregation_period: str = Field(default="hourly", description="Period for aggregation (hourly, daily, weekly, monthly)")
    sample_size: Optional[int] = Field(None, description="Number of data points in this aggregation")

    # Customer Experience Metrics (when applicable)
    csat_score: Optional[float] = Field(None, description="Customer Satisfaction Score (1-5 scale)")
    nps_score: Optional[int] = Field(None, description="Net Promoter Score (-100 to 100)")
    sentiment_distribution: Optional[Dict[str, float]] = Field(None, description="Distribution of sentiment types")

    # Operational Efficiency Metrics (when applicable)
    containment_rate: Optional[float] = Field(None, description="Percentage of conversations handled without human escalation")
    resolution_rate: Optional[float] = Field(None, description="Percentage of issues successfully resolved")
    human_handoff_rate: Optional[float] = Field(None, description="Percentage of conversations escalated to humans")
    fallback_rate: Optional[float] = Field(None, description="Percentage of conversations with fallback responses")
    average_handling_time_seconds: Optional[float] = Field(None, description="Average time to resolve conversations")
    cost_per_conversation: Optional[float] = Field(None, description="Operational cost per automated conversation")

    # Engagement & Usage Metrics (when applicable)
    active_users_count: Optional[int] = Field(None, description="Number of active users in the period")
    retention_rate: Optional[float] = Field(None, description="Percentage of users returning")
    conversation_completion_rate: Optional[float] = Field(None, description="Percentage of completed conversations")
    total_conversations: Optional[int] = Field(None, description="Total number of conversations")
    bounce_rate: Optional[float] = Field(None, description="Percentage of single-message conversations")
    goal_completion_rate: Optional[float] = Field(None, description="Percentage of users achieving goals")

    # Performance Metrics
    error_rate: Optional[float] = Field(None, description="Percentage of conversations with errors")
    average_latency_ms: Optional[float] = Field(None, description="Average response latency in milliseconds")
    conversation_length_avg: Optional[float] = Field(None, description="Average number of messages per conversation")

    # Metadata and context
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metric metadata and context")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class CustomerFeedback(BaseModel):
    """Stores customer feedback and satisfaction ratings."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for the feedback")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")

    interaction_id: str = Field(..., description="Linked bot interaction")
    user_id: Optional[uuid.UUID] = Field(None, description="User who provided feedback")
    group_id: Optional[str] = Field(None, description="Group where feedback was collected")

    # Feedback types
    csat_rating: Optional[int] = Field(None, description="CSAT rating (1-5 scale)")
    nps_rating: Optional[int] = Field(None, description="NPS rating (0-10 scale)")
    helpful_rating: Optional[bool] = Field(None, description="Was this interaction helpful?")
    feedback_text: Optional[str] = Field(None, description="Optional written feedback")

    # Context
    conversation_context: Dict[str, Any] = Field(default_factory=dict, description="Context from the conversation")
    bot_responses: List[str] = Field(default_factory=list, description="Bot responses in the conversation")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class AggregatedKPIs(BaseModel):
    """Stores aggregated KPIs for reporting and analysis."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for the KPI aggregation")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")

    # Time period
    period_start: datetime = Field(..., description="Start of the aggregation period")
    period_end: datetime = Field(..., description="End of the aggregation period")
    period_type: str = Field(..., description="Type of period (daily, weekly, monthly)")

    bot_id: Optional[str] = Field(None, description="Specific bot, if aggregated per bot")
    group_id: Optional[str] = Field(None, description="Specific group, if aggregated per group")

    # Aggregated metrics
    total_conversations: int = Field(default=0, description="Total conversations in the period")
    unique_users: int = Field(default=0, description="Unique users who interacted")

    # Customer Experience
    avg_csat: Optional[float] = Field(None, description="Average CSAT score")
    avg_nps: Optional[float] = Field(None, description="Average NPS score")
    positive_sentiment_rate: Optional[float] = Field(None, description="Percentage of positive sentiment interactions")

    # Operational Efficiency
    containment_rate: Optional[float] = Field(None, description="Overall containment rate")
    resolution_rate: Optional[float] = Field(None, description="Overall resolution rate")
    avg_handling_time_seconds: Optional[float] = Field(None, description="Average handling time")
    total_cost_saved: Optional[float] = Field(None, description="Estimated cost savings from automation")

    # Engagement & Usage
    completion_rate: Optional[float] = Field(None, description="Conversation completion rate")
    bounce_rate: Optional[float] = Field(None, description="Overall bounce rate")
    retention_rate: Optional[float] = Field(None, description="User retention rate")

    # Performance
    error_rate: Optional[float] = Field(None, description="Overall error rate")
    avg_latency_ms: Optional[float] = Field(None, description="Average response latency")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional aggregation metadata")

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        orm_mode = True

class ConversionTracking(BaseModel):
    """Tracks bot-initiated conversions, checkouts, and user outcomes."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique ID for the conversion tracking")
    tenant_id: uuid.UUID = Field(..., description="Foreign key to the Tenant")

    # Interaction context
    interaction_id: str = Field(..., description="Linked bot interaction that initiated the conversion")
    bot_id: str = Field(..., description="Bot that facilitated the conversion")

    # Trigger and intent analysis
    trigger_message: str = Field(..., description="The user's message that triggered the conversion flow")
    intent_score: float = Field(..., description="Confidence score of the detected user intent (0-1)")
    detected_intent: str = Field(..., description="The AI-detected user intent (e.g., 'purchase', 'inquiry', 'support')")

    # Bot response
    bot_message: str = Field(..., description="The bot's response message that led to the conversion")
    response_confidence: float = Field(..., description="Bot's confidence in its response (0-1)")

    # Conversion details
    conversion_type: str = Field(..., description="Type of conversion (checkout, signup, download, visit)")
    conversion_value: Optional[float] = Field(None, description="Monetary value of the conversion if applicable")
    currency: str = Field(default="USD", description="Currency for the conversion value")

    # Outcome tracking
    outcome: str = Field(..., description="Final user action (purchased, visited, did_nothing, abandoned)")
    time_to_conversion_seconds: Optional[int] = Field(None, description="Time from trigger to conversion completion")
    checkout_completed: bool = Field(default=False, description="Whether the checkout process was fully completed")

    # Additional tracking
    referral_source: Optional[str] = Field(None, description="Source that led to the conversion (e.g., affiliate_link, sponsored_content)")
    monetization_source_id: Optional[str] = Field(None, description="Linked monetization source if applicable")

    # Performance metrics
    conversion_rate: float = Field(default=0.0, description="Conversion rate for this interaction type")
    abandonment_rate: float = Field(default=0.0, description="Rate at which users abandon after this point")

    # User journey tracking
    pages_visited: List[str] = Field(default_factory=list, description="Pages or steps visited during the conversion process")
    actions_taken: List[str] = Field(default_factory=list, description="Specific actions taken by the user")

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional conversion tracking metadata")

    created_at: datetime = Field(default_factory=datetime.utcnow)
    converted_at: Optional[datetime] = Field(None, description="When the conversion was completed")

    class Config:
        orm_mode = True
