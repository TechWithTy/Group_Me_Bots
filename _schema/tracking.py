"""
Pydantic types for knowledge base calls and MCP (Model Context Protocol) tracking.

This module defines comprehensive type models for tracking:
- Knowledge base interactions and calls
- MCP server interactions and tool usage
- Browser interactions and web scraping activities
- Analytics and performance metrics for all tracked operations

Used for monitoring, analytics, and optimization of AI-powered workflows.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4


# Enums for tracking categories

class KnowledgeBaseType(str, Enum):
    """Types of knowledge bases that can be queried."""
    DOCUMENTATION = "documentation"
    WIKI = "wiki"
    FAQ = "faq"
    CODEBASE = "codebase"
    API_REFERENCE = "api_reference"
    TUTORIAL = "tutorial"
    CUSTOM = "custom"

class MCPServerType(str, Enum):
    """Types of MCP servers."""
    FILESYSTEM = "filesystem"
    DATABASE = "database"
    WEB_API = "web_api"
    SEARCH_ENGINE = "search_engine"
    CODE_EXECUTION = "code_execution"
    CUSTOM_TOOL = "custom_tool"

class InteractionStatus(str, Enum):
    """Status of tracked interactions."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

class BrowserAction(str, Enum):
    """Types of browser actions."""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    EXTRACT = "extract"

# Base tracking models

class BaseTrackingModel(BaseModel):
    """Base model for all tracking entities."""
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    tenant_id: str
    session_id: str
    user_id: Optional[str] = None

class KnowledgeBaseCall(BaseTrackingModel):
    """Tracks knowledge base queries and responses."""

    kb_type: KnowledgeBaseType
    kb_identifier: str  # ID or name of the knowledge base
    query: str
    context: Optional[str] = None
    response: Optional[str] = None
    response_metadata: Optional[Dict[str, Any]] = None

    # Performance metrics
    response_time_ms: Optional[int] = None
    tokens_used: Optional[int] = None
    status: InteractionStatus = InteractionStatus.PENDING

    # Additional metadata
    query_embedding: Optional[List[float]] = None
    response_confidence: Optional[float] = None
    source_documents: Optional[List[str]] = None

class MCPCall(BaseTrackingModel):
    """Tracks MCP server interactions and tool usage."""

    server_name: str
    server_type: MCPServerType
    tool_name: str
    tool_parameters: Dict[str, Any]
    tool_response: Optional[Any] = None

    # Performance metrics
    execution_time_ms: Optional[int] = None
    status: InteractionStatus = InteractionStatus.PENDING
    error_message: Optional[str] = None

    # Tool-specific metadata
    tool_version: Optional[str] = None
    tool_category: Optional[str] = None

class BrowserInteraction(BaseTrackingModel):
    """Tracks browser automation and web scraping activities."""

    url: str
    action: BrowserAction
    action_parameters: Dict[str, Any]
    result: Optional[Any] = None

    # Browser context
    browser_type: str = "chromium"  # chromium, firefox, webkit
    viewport_size: Optional[Dict[str, int]] = None

    # Performance metrics
    load_time_ms: Optional[int] = None
    status: InteractionStatus = InteractionStatus.PENDING

    # Content extraction
    extracted_text: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    screenshots: Optional[List[str]] = None  # Base64 encoded images

# Analytics and aggregation models

class KnowledgeBaseAnalytics(BaseModel):
    """Analytics for knowledge base usage."""

    tenant_id: str
    kb_type: KnowledgeBaseType
    kb_identifier: str

    # Usage statistics
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0

    # Performance metrics
    avg_response_time_ms: float = 0.0
    avg_tokens_used: float = 0.0
    avg_confidence_score: float = 0.0

    # Time period
    period_start: datetime
    period_end: datetime

    # Popular queries
    top_queries: List[Dict[str, Any]] = Field(default_factory=list)
    query_frequency: Dict[str, int] = Field(default_factory=dict)

class MCPAnalytics(BaseModel):
    """Analytics for MCP server usage."""

    tenant_id: str
    server_name: str
    server_type: MCPServerType

    # Usage statistics
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0

    # Performance metrics
    avg_execution_time_ms: float = 0.0

    # Tool usage
    tools_used: Dict[str, int] = Field(default_factory=dict)
    tool_performance: Dict[str, Dict[str, float]] = Field(default_factory=dict)

    # Time period
    period_start: datetime
    period_end: datetime

class BrowserAnalytics(BaseModel):
    """Analytics for browser interactions."""

    tenant_id: str

    # Usage statistics
    total_sessions: int = 0
    total_actions: int = 0
    successful_actions: int = 0

    # Performance metrics
    avg_page_load_time_ms: float = 0.0
    avg_session_duration_ms: float = 0.0

    # Action breakdown
    actions_by_type: Dict[str, int] = Field(default_factory=dict)
    top_domains: List[Dict[str, Any]] = Field(default_factory=list)

    # Error tracking
    error_rate: float = 0.0
    common_errors: Dict[str, int] = Field(default_factory=dict)

    # Time period
    period_start: datetime
    period_end: datetime

# Request/Response models for API endpoints

class KnowledgeBaseQueryRequest(BaseModel):
    """Request model for knowledge base queries."""

    kb_type: KnowledgeBaseType
    kb_identifier: str
    query: str
    context: Optional[str] = None
    max_tokens: Optional[int] = 1000
    temperature: Optional[float] = 0.7

class KnowledgeBaseQueryResponse(BaseModel):
    """Response model for knowledge base queries."""

    call_id: UUID
    response: str
    response_metadata: Optional[Dict[str, Any]] = None
    response_time_ms: int
    tokens_used: Optional[int] = None
    confidence_score: Optional[float] = None
    source_documents: Optional[List[str]] = None

class MCPCallRequest(BaseModel):
    """Request model for MCP tool calls."""

    server_name: str
    tool_name: str
    parameters: Dict[str, Any]
    timeout_seconds: Optional[int] = 30

class MCPCallResponse(BaseModel):
    """Response model for MCP tool calls."""

    call_id: UUID
    result: Any
    execution_time_ms: int
    tool_version: Optional[str] = None

class BrowserActionRequest(BaseModel):
    """Request model for browser actions."""

    url: str
    action: BrowserAction
    parameters: Dict[str, Any]
    wait_for_selector: Optional[str] = None
    timeout_seconds: Optional[int] = 30

class BrowserActionResponse(BaseModel):
    """Response model for browser actions."""

    interaction_id: UUID
    result: Any
    load_time_ms: Optional[int] = None
    extracted_data: Optional[Dict[str, Any]] = None
    screenshot: Optional[str] = None

# Batch operation models

class BatchKnowledgeBaseRequest(BaseModel):
    """Request model for batch knowledge base queries."""

    queries: List[KnowledgeBaseQueryRequest]
    parallel_execution: bool = True

class BatchKnowledgeBaseResponse(BaseModel):
    """Response model for batch knowledge base queries."""

    batch_id: UUID
    results: List[KnowledgeBaseQueryResponse]
    total_time_ms: int
    successful_queries: int
    failed_queries: int

class BatchMCPRequest(BaseModel):
    """Request model for batch MCP tool calls."""

    calls: List[MCPCallRequest]
    parallel_execution: bool = True

class BatchMCPResponse(BaseModel):
    """Response model for batch MCP tool calls."""

    batch_id: UUID
    results: List[MCPCallResponse]
    total_time_ms: int
    successful_calls: int
    failed_calls: int

# Configuration models

class KnowledgeBaseConfig(BaseModel):
    """Configuration for knowledge base connections."""

    kb_type: KnowledgeBaseType
    kb_identifier: str
    connection_url: Optional[str] = None
    api_key: Optional[str] = None
    authentication: Optional[Dict[str, Any]] = None
    settings: Dict[str, Any] = Field(default_factory=dict)

class MCPServerConfig(BaseModel):
    """Configuration for MCP server connections."""

    server_name: str
    server_type: MCPServerType
    connection_url: str
    authentication: Optional[Dict[str, Any]] = None
    capabilities: List[str] = Field(default_factory=list)
    settings: Dict[str, Any] = Field(default_factory=dict)

class BrowserConfig(BaseModel):
    """Configuration for browser automation."""

    browser_type: str = "chromium"
    headless: bool = True
    viewport_width: int = 1280
    viewport_height: int = 720
    user_agent: Optional[str] = None
    proxy_config: Optional[Dict[str, Any]] = None
    settings: Dict[str, Any] = Field(default_factory=dict)

# Error models

class TrackingError(BaseModel):
    """Error information for failed operations."""

    error_code: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class KnowledgeBaseError(TrackingError):
    """Knowledge base specific errors."""

    kb_type: KnowledgeBaseType
    kb_identifier: str
    query: Optional[str] = None

class MCPError(TrackingError):
    """MCP server specific errors."""

    server_name: str
    tool_name: str
    parameters: Optional[Dict[str, Any]] = None

class BrowserError(TrackingError):
    """Browser automation specific errors."""

    url: str
    action: BrowserAction
    parameters: Optional[Dict[str, Any]] = None

# Validation helpers

def validate_uuid_string(uuid_str: str) -> bool:
    """Validate that a string is a valid UUID."""
    try:
        UUID(uuid_str)
        return True
    except ValueError:
        return False

def validate_knowledge_base_type(kb_type: str) -> bool:
    """Validate knowledge base type."""
    return kb_type in [e.value for e in KnowledgeBaseType]

def validate_mcp_server_type(server_type: str) -> bool:
    """Validate MCP server type."""
    return server_type in [e.value for e in MCPServerType]

def validate_browser_action(action: str) -> bool:
    """Validate browser action."""
    return action in [e.value for e in BrowserAction]

# Export all models for easy importing

__all__ = [
    # Enums
    "KnowledgeBaseType",
    "MCPServerType",
    "InteractionStatus",
    "BrowserAction",

    # Tracking models
    "BaseTrackingModel",
    "KnowledgeBaseCall",
    "MCPCall",
    "BrowserInteraction",

    # Analytics models
    "KnowledgeBaseAnalytics",
    "MCPAnalytics",
    "BrowserAnalytics",

    # API models
    "KnowledgeBaseQueryRequest",
    "KnowledgeBaseQueryResponse",
    "MCPCallRequest",
    "MCPCallResponse",
    "BrowserActionRequest",
    "BrowserActionResponse",

    # Batch models
    "BatchKnowledgeBaseRequest",
    "BatchKnowledgeBaseResponse",
    "BatchMCPRequest",
    "BatchMCPResponse",

    # Configuration models
    "KnowledgeBaseConfig",
    "MCPServerConfig",
    "BrowserConfig",

    # Error models
    "TrackingError",
    "KnowledgeBaseError",
    "MCPError",
    "BrowserError",

    # Validation helpers
    "validate_uuid_string",
    "validate_knowledge_base_type",
    "validate_mcp_server_type",
    "validate_browser_action",
]
