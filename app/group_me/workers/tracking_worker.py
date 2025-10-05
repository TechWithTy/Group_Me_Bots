"""
Tracking Worker for knowledge base calls and MCP interactions.

This worker provides comprehensive tracking and analytics for:
- Knowledge base queries and responses
- MCP server tool usage and performance
- Browser automation activities
- Performance monitoring and optimization

Implements real-time tracking, analytics generation, and performance optimization
for AI-powered workflows and browser automation systems.
"""
from __future__ import annotations

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from uuid import UUID, uuid4

from pydantic import ValidationError

from app.models import Group, Member
from workers.base_worker import BaseWorker
from _schema.tracking import (
    KnowledgeBaseCall, MCPCall, BrowserInteraction,
    KnowledgeBaseAnalytics, MCPAnalytics, BrowserAnalytics,
    KnowledgeBaseQueryRequest, KnowledgeBaseQueryResponse,
    MCPCallRequest, MCPCallResponse,
    BrowserActionRequest, BrowserActionResponse,
    KnowledgeBaseType, MCPServerType, InteractionStatus, BrowserAction,
    KnowledgeBaseConfig, MCPServerConfig, BrowserConfig,
    TrackingError, KnowledgeBaseError, MCPError, BrowserError
)

logger = logging.getLogger(__name__)


class TrackingWorker(BaseWorker):
    """
    Advanced worker for tracking knowledge base calls and MCP interactions.

    Provides comprehensive monitoring, analytics, and performance optimization
    for AI-powered workflows, browser automation, and external service integrations.
    """

    def __init__(self, groupme_client, db_session):
        super().__init__(groupme_client, db_session)

        # Tracking storage
        self.knowledge_base_calls: List[KnowledgeBaseCall] = []
        self.mcp_calls: List[MCPCall] = []
        self.browser_interactions: List[BrowserInteraction] = []

        # Configuration storage
        self.kb_configs: Dict[str, KnowledgeBaseConfig] = {}
        self.mcp_configs: Dict[str, MCPServerConfig] = {}
        self.browser_config: Optional[BrowserConfig] = None

        # Analytics caches
        self.kb_analytics_cache: Dict[str, KnowledgeBaseAnalytics] = {}
        self.mcp_analytics_cache: Dict[str, MCPAnalytics] = {}
        self.browser_analytics_cache: Optional[BrowserAnalytics] = None

        # Performance monitoring
        self.performance_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)

    async def initialize(self) -> None:
        """Initialize the tracking worker."""
        logger.info("Initializing TrackingWorker")

        # Load configurations
        await self._load_configurations()

        # Start analytics processor
        asyncio.create_task(self._process_analytics())

        logger.info("TrackingWorker initialization complete")

    async def _load_configurations(self) -> None:
        """Load tracking configurations."""
        # Load knowledge base configurations
        self.kb_configs = {
            "default_docs": KnowledgeBaseConfig(
                kb_type=KnowledgeBaseType.DOCUMENTATION,
                kb_identifier="default",
                settings={"max_tokens": 1000, "temperature": 0.7}
            )
        }

        # Load MCP server configurations
        self.mcp_configs = {
            "filesystem": MCPServerConfig(
                server_name="filesystem",
                server_type=MCPServerType.FILESYSTEM,
                connection_url="local://",
                capabilities=["read_file", "list_dir", "search"]
            ),
            "web_search": MCPServerConfig(
                server_name="web_search",
                server_type=MCPServerType.SEARCH_ENGINE,
                connection_url="https://api.example.com/search",
                capabilities=["search", "summarize"]
            )
        }

        # Load browser configuration
        self.browser_config = BrowserConfig(
            browser_type="chromium",
            headless=True,
            viewport_width=1280,
            viewport_height=720
        )

    # Knowledge Base Tracking Methods

    async def track_knowledge_base_call(
        self,
        kb_type: KnowledgeBaseType,
        kb_identifier: str,
        query: str,
        context: Optional[str] = None,
        response: Optional[str] = None,
        **kwargs
    ) -> UUID:
        """Track a knowledge base call."""
        call_id = uuid4()

        call = KnowledgeBaseCall(
            id=call_id,
            tenant_id=self.tenant_id,
            session_id=getattr(self, 'session_id', 'default'),
            kb_type=kb_type,
            kb_identifier=kb_identifier,
            query=query,
            context=context,
            response=response,
            **kwargs
        )

        self.knowledge_base_calls.append(call)

        # Update analytics
        await self._update_knowledge_base_analytics(call)

        logger.info(f"Tracked KB call {call_id} for {kb_type.value}")
        return call_id

    async def query_knowledge_base(
        self,
        request: KnowledgeBaseQueryRequest
    ) -> KnowledgeBaseQueryResponse:
        """Execute a knowledge base query with tracking."""
        start_time = time.time()

        try:
            # Simulate knowledge base query
            await asyncio.sleep(0.1)  # Simulate processing time

            response_text = f"Response to: {request.query}"
            response_time_ms = int((time.time() - start_time) * 1000)

            # Track the call
            call_id = await self.track_knowledge_base_call(
                kb_type=request.kb_type,
                kb_identifier=request.kb_identifier,
                query=request.query,
                context=request.context,
                response=response_text,
                response_time_ms=response_time_ms,
                status=InteractionStatus.COMPLETED
            )

            return KnowledgeBaseQueryResponse(
                call_id=call_id,
                response=response_text,
                response_time_ms=response_time_ms,
                tokens_used=100  # Mock value
            )

        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)

            # Track failed call
            await self.track_knowledge_base_call(
                kb_type=request.kb_type,
                kb_identifier=request.kb_identifier,
                query=request.query,
                context=request.context,
                status=InteractionStatus.FAILED,
                response_time_ms=response_time_ms
            )

            raise

    # MCP Call Tracking Methods

    async def track_mcp_call(
        self,
        server_name: str,
        tool_name: str,
        parameters: Dict[str, Any],
        response: Optional[Any] = None,
        **kwargs
    ) -> UUID:
        """Track an MCP server call."""
        call_id = uuid4()

        call = MCPCall(
            id=call_id,
            tenant_id=self.tenant_id,
            session_id=getattr(self, 'session_id', 'default'),
            server_name=server_name,
            tool_name=tool_name,
            tool_parameters=parameters,
            tool_response=response,
            **kwargs
        )

        self.mcp_calls.append(call)

        # Update analytics
        await self._update_mcp_analytics(call)

        logger.info(f"Tracked MCP call {call_id} for {server_name}.{tool_name}")
        return call_id

    async def call_mcp_tool(
        self,
        request: MCPCallRequest
    ) -> MCPCallResponse:
        """Execute an MCP tool call with tracking."""
        start_time = time.time()

        try:
            # Simulate MCP tool execution
            await asyncio.sleep(0.05)  # Simulate processing time

            # Mock response based on tool name
            if request.tool_name == "read_file":
                result = {"content": "Mock file content", "size": 1024}
            elif request.tool_name == "search":
                result = {"results": ["result1", "result2"], "total": 2}
            else:
                result = {"status": "success", "data": "mock_response"}

            execution_time_ms = int((time.time() - start_time) * 1000)

            # Track the call
            call_id = await self.track_mcp_call(
                server_name=request.server_name,
                tool_name=request.tool_name,
                parameters=request.parameters,
                response=result,
                execution_time_ms=execution_time_ms,
                status=InteractionStatus.COMPLETED
            )

            return MCPCallResponse(
                call_id=call_id,
                result=result,
                execution_time_ms=execution_time_ms
            )

        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)

            # Track failed call
            await self.track_mcp_call(
                server_name=request.server_name,
                tool_name=request.tool_name,
                parameters=request.parameters,
                status=InteractionStatus.FAILED,
                execution_time_ms=execution_time_ms,
                error_message=str(e)
            )

            raise

    # Browser Interaction Tracking Methods

    async def track_browser_interaction(
        self,
        url: str,
        action: BrowserAction,
        parameters: Dict[str, Any],
        result: Optional[Any] = None,
        **kwargs
    ) -> UUID:
        """Track a browser interaction."""
        interaction_id = uuid4()

        interaction = BrowserInteraction(
            id=interaction_id,
            tenant_id=self.tenant_id,
            session_id=getattr(self, 'session_id', 'default'),
            url=url,
            action=action,
            action_parameters=parameters,
            result=result,
            browser_type=self.browser_config.browser_type if self.browser_config else "chromium",
            **kwargs
        )

        self.browser_interactions.append(interaction)

        # Update analytics
        await self._update_browser_analytics(interaction)

        logger.info(f"Tracked browser interaction {interaction_id} for {action.value} on {url}")
        return interaction_id

    async def execute_browser_action(
        self,
        request: BrowserActionRequest
    ) -> BrowserActionResponse:
        """Execute a browser action with tracking."""
        start_time = time.time()

        try:
            # Simulate browser action
            await asyncio.sleep(0.2)  # Simulate browser processing

            load_time_ms = int((time.time() - start_time) * 1000)

            # Mock result based on action
            if request.action == BrowserAction.NAVIGATE:
                result = {"title": "Mock Page Title", "status": "loaded"}
            elif request.action == BrowserAction.EXTRACT:
                result = {"text": "Extracted content", "links": ["link1", "link2"]}
            else:
                result = {"status": "success"}

            # Track the interaction
            interaction_id = await self.track_browser_interaction(
                url=request.url,
                action=request.action,
                parameters=request.parameters,
                result=result,
                load_time_ms=load_time_ms,
                status=InteractionStatus.COMPLETED
            )

            return BrowserActionResponse(
                interaction_id=interaction_id,
                result=result,
                load_time_ms=load_time_ms,
                extracted_data=result if request.action == BrowserAction.EXTRACT else None
            )

        except Exception as e:
            load_time_ms = int((time.time() - start_time) * 1000)

            # Track failed interaction
            await self.track_browser_interaction(
                url=request.url,
                action=request.action,
                parameters=request.parameters,
                status=InteractionStatus.FAILED,
                load_time_ms=load_time_ms
            )

            raise

    # Analytics Methods

    async def get_knowledge_base_analytics(
        self,
        kb_type: Optional[KnowledgeBaseType] = None,
        kb_identifier: Optional[str] = None,
        hours: int = 24
    ) -> List[KnowledgeBaseAnalytics]:
        """Get knowledge base analytics."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Filter calls by criteria
        filtered_calls = [
            call for call in self.knowledge_base_calls
            if call.timestamp >= cutoff_time
            and (kb_type is None or call.kb_type == kb_type)
            and (kb_identifier is None or call.kb_identifier == kb_identifier)
        ]

        if not filtered_calls:
            return []

        # Group by kb_type and identifier
        grouped_calls = defaultdict(list)
        for call in filtered_calls:
            key = f"{call.kb_type.value}_{call.kb_identifier}"
            grouped_calls[key].append(call)

        # Generate analytics for each group
        analytics_list = []
        for key, calls in grouped_calls.items():
            kb_type_str, kb_identifier = key.split("_", 1)

            # Calculate metrics
            successful_calls = [c for c in calls if c.status == InteractionStatus.COMPLETED]
            failed_calls = [c for c in calls if c.status == InteractionStatus.FAILED]

            avg_response_time = sum(c.response_time_ms for c in successful_calls if c.response_time_ms) / len(successful_calls) if successful_calls else 0
            avg_tokens = sum(c.tokens_used for c in successful_calls if c.tokens_used) / len(successful_calls) if successful_calls else 0
            avg_confidence = sum(c.response_confidence for c in successful_calls if c.response_confidence) / len(successful_calls) if successful_calls else 0

            analytics = KnowledgeBaseAnalytics(
                tenant_id=self.tenant_id,
                kb_type=KnowledgeBaseType(kb_type_str),
                kb_identifier=kb_identifier,
                total_calls=len(calls),
                successful_calls=len(successful_calls),
                failed_calls=len(failed_calls),
                avg_response_time_ms=avg_response_time,
                avg_tokens_used=avg_tokens,
                avg_confidence_score=avg_confidence,
                period_start=min(c.timestamp for c in calls),
                period_end=max(c.timestamp for c in calls)
            )

            analytics_list.append(analytics)

        return analytics_list

    async def get_mcp_analytics(
        self,
        server_name: Optional[str] = None,
        hours: int = 24
    ) -> List[MCPAnalytics]:
        """Get MCP server analytics."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Filter calls by criteria
        filtered_calls = [
            call for call in self.mcp_calls
            if call.timestamp >= cutoff_time
            and (server_name is None or call.server_name == server_name)
        ]

        if not filtered_calls:
            return []

        # Group by server
        grouped_calls = defaultdict(list)
        for call in filtered_calls:
            grouped_calls[call.server_name].append(call)

        # Generate analytics for each server
        analytics_list = []
        for server_name, calls in grouped_calls.items():
            server_config = self.mcp_configs.get(server_name)
            if not server_config:
                continue

            successful_calls = [c for c in calls if c.status == InteractionStatus.COMPLETED]
            failed_calls = [c for c in calls if c.status == InteractionStatus.FAILED]

            avg_execution_time = sum(c.execution_time_ms for c in successful_calls if c.execution_time_ms) / len(successful_calls) if successful_calls else 0

            # Tool usage statistics
            tools_used = Counter(c.tool_name for c in calls)
            tool_performance = defaultdict(dict)
            for call in successful_calls:
                if call.execution_time_ms:
                    tool_performance[call.tool_name]["avg_time"] = tool_performance[call.tool_name].get("avg_time", 0) + call.execution_time_ms

            for tool, perf in tool_performance.items():
                if tools_used[tool] > 0:
                    perf["avg_time"] /= tools_used[tool]

            analytics = MCPAnalytics(
                tenant_id=self.tenant_id,
                server_name=server_name,
                server_type=server_config.server_type,
                total_calls=len(calls),
                successful_calls=len(successful_calls),
                failed_calls=len(failed_calls),
                avg_execution_time_ms=avg_execution_time,
                tools_used=dict(tools_used),
                tool_performance=dict(tool_performance),
                period_start=min(c.timestamp for c in calls),
                period_end=max(c.timestamp for c in calls)
            )

            analytics_list.append(analytics)

        return analytics_list

    async def get_browser_analytics(self, hours: int = 24) -> Optional[BrowserAnalytics]:
        """Get browser interaction analytics."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        # Filter interactions
        filtered_interactions = [
            interaction for interaction in self.browser_interactions
            if interaction.timestamp >= cutoff_time
        ]

        if not filtered_interactions:
            return None

        successful_interactions = [i for i in filtered_interactions if i.status == InteractionStatus.COMPLETED]

        # Calculate metrics
        total_sessions = len(set(i.session_id for i in filtered_interactions))
        total_actions = len(filtered_interactions)

        avg_load_time = sum(i.load_time_ms for i in successful_interactions if i.load_time_ms) / len(successful_interactions) if successful_interactions else 0

        # Action breakdown
        actions_by_type = Counter(i.action.value for i in filtered_interactions)

        # Domain analysis
        domains = Counter()
        for interaction in filtered_interactions:
            try:
                from urllib.parse import urlparse
                domain = urlparse(interaction.url).netloc
                domains[domain] += 1
            except:
                pass

        top_domains = [{"domain": domain, "count": count} for domain, count in domains.most_common(10)]

        # Error analysis
        failed_interactions = [i for i in filtered_interactions if i.status == InteractionStatus.FAILED]
        error_rate = len(failed_interactions) / total_actions if total_actions > 0 else 0

        analytics = BrowserAnalytics(
            tenant_id=self.tenant_id,
            total_sessions=total_sessions,
            total_actions=total_actions,
            successful_actions=len(successful_interactions),
            avg_page_load_time_ms=avg_load_time,
            actions_by_type=dict(actions_by_type),
            top_domains=top_domains,
            error_rate=error_rate,
            period_start=min(i.timestamp for i in filtered_interactions),
            period_end=max(i.timestamp for i in filtered_interactions)
        )

        return analytics

    # Private Analytics Update Methods

    async def _update_knowledge_base_analytics(self, call: KnowledgeBaseCall) -> None:
        """Update knowledge base analytics for a call."""
        cache_key = f"{call.kb_type.value}_{call.kb_identifier}"

        if cache_key not in self.kb_analytics_cache:
            self.kb_analytics_cache[cache_key] = KnowledgeBaseAnalytics(
                tenant_id=self.tenant_id,
                kb_type=call.kb_type,
                kb_identifier=call.kb_identifier,
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow()
            )

        # Update metrics (simplified - in production, use more sophisticated calculations)
        analytics = self.kb_analytics_cache[cache_key]
        analytics.total_calls += 1

        if call.status == InteractionStatus.COMPLETED:
            analytics.successful_calls += 1
        elif call.status == InteractionStatus.FAILED:
            analytics.failed_calls += 1

    async def _update_mcp_analytics(self, call: MCPCall) -> None:
        """Update MCP analytics for a call."""
        cache_key = call.server_name

        if cache_key not in self.mcp_analytics_cache:
            server_config = self.mcp_configs.get(call.server_name)
            if not server_config:
                return

            self.mcp_analytics_cache[cache_key] = MCPAnalytics(
                tenant_id=self.tenant_id,
                server_name=call.server_name,
                server_type=server_config.server_type,
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow()
            )

        # Update metrics
        analytics = self.mcp_analytics_cache[cache_key]
        analytics.total_calls += 1

        if call.status == InteractionStatus.COMPLETED:
            analytics.successful_calls += 1
        elif call.status == InteractionStatus.FAILED:
            analytics.failed_calls += 1

    async def _update_browser_analytics(self, interaction: BrowserInteraction) -> None:
        """Update browser analytics for an interaction."""
        # Simplified - in production, maintain a single browser analytics object
        pass

    # Analytics Processing

    async def _process_analytics(self) -> None:
        """Process and update analytics periodically."""
        while self.is_running:
            try:
                # Update knowledge base analytics
                await self._refresh_knowledge_base_analytics()

                # Update MCP analytics
                await self._refresh_mcp_analytics()

                # Update browser analytics
                await self._refresh_browser_analytics()

                # Clean up old data (keep last 7 days)
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                self.knowledge_base_calls = [c for c in self.knowledge_base_calls if c.timestamp >= cutoff_time]
                self.mcp_calls = [c for c in self.mcp_calls if c.timestamp >= cutoff_time]
                self.browser_interactions = [i for i in self.browser_interactions if i.timestamp >= cutoff_time]

                await asyncio.sleep(3600)  # Process every hour

            except Exception as e:
                logger.error(f"Error in analytics processing: {e}")
                await asyncio.sleep(3600)

    async def _refresh_knowledge_base_analytics(self) -> None:
        """Refresh knowledge base analytics cache."""
        # Clear existing cache
        self.kb_analytics_cache.clear()

        # Recalculate from recent calls
        recent_calls = [c for c in self.knowledge_base_calls if (datetime.utcnow() - c.timestamp) < timedelta(hours=24)]
        for call in recent_calls:
            await self._update_knowledge_base_analytics(call)

    async def _refresh_mcp_analytics(self) -> None:
        """Refresh MCP analytics cache."""
        # Clear existing cache
        self.mcp_analytics_cache.clear()

        # Recalculate from recent calls
        recent_calls = [c for c in self.mcp_calls if (datetime.utcnow() - c.timestamp) < timedelta(hours=24)]
        for call in recent_calls:
            await self._update_mcp_analytics(call)

    async def _refresh_browser_analytics(self) -> None:
        """Refresh browser analytics cache."""
        # Simplified - in production, calculate from recent interactions
        pass

    # Public Analytics Access

    async def get_comprehensive_analytics(self) -> Dict[str, Any]:
        """Get comprehensive analytics for all tracked systems."""
        return {
            "knowledge_base": await self.get_knowledge_base_analytics(hours=24),
            "mcp": await self.get_mcp_analytics(hours=24),
            "browser": await self.get_browser_analytics(hours=24),
            "summary": {
                "total_kb_calls": len(self.knowledge_base_calls),
                "total_mcp_calls": len(self.mcp_calls),
                "total_browser_interactions": len(self.browser_interactions),
                "generated_at": datetime.utcnow().isoformat()
            }
        }

    # Configuration Management

    def update_knowledge_base_config(self, config: KnowledgeBaseConfig) -> None:
        """Update knowledge base configuration."""
        key = f"{config.kb_type.value}_{config.kb_identifier}"
        self.kb_configs[key] = config
        logger.info(f"Updated KB config for {key}")

    def update_mcp_server_config(self, config: MCPServerConfig) -> None:
        """Update MCP server configuration."""
        self.mcp_configs[config.server_name] = config
        logger.info(f"Updated MCP config for {config.server_name}")

    def update_browser_config(self, config: BrowserConfig) -> None:
        """Update browser configuration."""
        self.browser_config = config
        logger.info("Updated browser configuration")

    # Error Tracking

    async def track_error(
        self,
        error_type: str,
        error: Exception,
        context: Dict[str, Any]
    ) -> None:
        """Track an error with context."""
        error_info = TrackingError(
            error_code=error_type,
            error_message=str(error),
            error_details=context,
            timestamp=datetime.utcnow()
        )

        # Log error for monitoring
        logger.error(f"Tracked error {error_type}: {error}", extra={"error_details": context})

    async def start_worker(self) -> None:
        """Start the tracking worker."""
        logger.info("Starting TrackingWorker")

        await self.initialize()

        # Keep worker alive
        while self.is_running:
            await asyncio.sleep(10)

    async def stop_worker(self) -> None:
        """Stop the tracking worker."""
        logger.info("Stopping TrackingWorker")
        self.is_running = False
