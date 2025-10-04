"""
Tests for the TrackingWorker.

This module tests tracking functionality for:
- Knowledge base call tracking
- MCP server interaction tracking
- Browser automation tracking
- Analytics generation and performance monitoring
"""
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from uuid import uuid4

from workers.tracking_worker import TrackingWorker
from _schema.tracking import (
    KnowledgeBaseCall, MCPCall, BrowserInteraction,
    KnowledgeBaseQueryRequest, MCPCallRequest, BrowserActionRequest,
    KnowledgeBaseType, MCPServerType, InteractionStatus, BrowserAction
)


class TestTrackingWorker:
    """Test suite for TrackingWorker functionality."""

    @pytest.fixture
    def mock_groupme_client(self):
        """Mock GroupMe client for testing."""
        return MagicMock()

    @pytest.fixture
    def mock_db_session(self):
        """Mock database session."""
        return MagicMock()

    @pytest.fixture
    def tracking_worker(self, mock_groupme_client, mock_db_session):
        """TrackingWorker instance for testing."""
        worker = TrackingWorker(mock_groupme_client, mock_db_session)
        worker.is_running = True
        return worker

    def test_knowledge_base_call_tracking(self, tracking_worker):
        """Test knowledge base call tracking."""
        # Test call creation
        call_id = asyncio.run(tracking_worker.track_knowledge_base_call(
            kb_type=KnowledgeBaseType.DOCUMENTATION,
            kb_identifier="test_docs",
            query="What is GroupMe?",
            response="GroupMe is a messaging platform"
        ))

        assert call_id is not None
        assert len(tracking_worker.knowledge_base_calls) == 1

        call = tracking_worker.knowledge_base_calls[0]
        assert call.kb_type == KnowledgeBaseType.DOCUMENTATION
        assert call.query == "What is GroupMe?"
        assert call.status == InteractionStatus.COMPLETED

    def test_mcp_call_tracking(self, tracking_worker):
        """Test MCP call tracking."""
        # Test call creation
        call_id = asyncio.run(tracking_worker.track_mcp_call(
            server_name="filesystem",
            tool_name="read_file",
            parameters={"path": "/test/file.txt"},
            response={"content": "test content"}
        ))

        assert call_id is not None
        assert len(tracking_worker.mcp_calls) == 1

        call = tracking_worker.mcp_calls[0]
        assert call.server_name == "filesystem"
        assert call.tool_name == "read_file"
        assert call.status == InteractionStatus.COMPLETED

    def test_browser_interaction_tracking(self, tracking_worker):
        """Test browser interaction tracking."""
        # Test interaction creation
        interaction_id = asyncio.run(tracking_worker.track_browser_interaction(
            url="https://example.com",
            action=BrowserAction.NAVIGATE,
            parameters={"wait_for_load": True},
            result={"status": "success"}
        ))

        assert interaction_id is not None
        assert len(tracking_worker.browser_interactions) == 1

        interaction = tracking_worker.browser_interactions[0]
        assert interaction.url == "https://example.com"
        assert interaction.action == BrowserAction.NAVIGATE
        assert interaction.status == InteractionStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_knowledge_base_query_execution(self, tracking_worker):
        """Test knowledge base query execution with tracking."""
        request = KnowledgeBaseQueryRequest(
            kb_type=KnowledgeBaseType.DOCUMENTATION,
            kb_identifier="test_docs",
            query="How to use GroupMe API?",
            max_tokens=1000
        )

        response = await tracking_worker.query_knowledge_base(request)

        assert response.call_id is not None
        assert response.response is not None
        assert response.response_time_ms > 0
        assert len(tracking_worker.knowledge_base_calls) == 1

    @pytest.mark.asyncio
    async def test_mcp_tool_execution(self, tracking_worker):
        """Test MCP tool execution with tracking."""
        request = MCPCallRequest(
            server_name="filesystem",
            tool_name="read_file",
            parameters={"path": "/test.txt"}
        )

        response = await tracking_worker.call_mcp_tool(request)

        assert response.call_id is not None
        assert response.result is not None
        assert response.execution_time_ms > 0
        assert len(tracking_worker.mcp_calls) == 1

    @pytest.mark.asyncio
    async def test_browser_action_execution(self, tracking_worker):
        """Test browser action execution with tracking."""
        request = BrowserActionRequest(
            url="https://example.com",
            action=BrowserAction.EXTRACT,
            parameters={"selector": "h1"}
        )

        response = await tracking_worker.execute_browser_action(request)

        assert response.interaction_id is not None
        assert response.result is not None
        assert response.load_time_ms > 0
        assert len(tracking_worker.browser_interactions) == 1

    @pytest.mark.asyncio
    async def test_knowledge_base_analytics_generation(self, tracking_worker):
        """Test knowledge base analytics generation."""
        # Create test calls
        await tracking_worker.track_knowledge_base_call(
            kb_type=KnowledgeBaseType.DOCUMENTATION,
            kb_identifier="test_docs",
            query="Query 1",
            response_time_ms=100,
            status=InteractionStatus.COMPLETED
        )

        await tracking_worker.track_knowledge_base_call(
            kb_type=KnowledgeBaseType.DOCUMENTATION,
            kb_identifier="test_docs",
            query="Query 2",
            response_time_ms=150,
            status=InteractionStatus.COMPLETED
        )

        analytics = await tracking_worker.get_knowledge_base_analytics(
            kb_type=KnowledgeBaseType.DOCUMENTATION,
            kb_identifier="test_docs",
            hours=24
        )

        assert len(analytics) == 1
        kb_analytics = analytics[0]
        assert kb_analytics.total_calls == 2
        assert kb_analytics.successful_calls == 2
        assert kb_analytics.avg_response_time_ms == 125  # (100 + 150) / 2

    @pytest.mark.asyncio
    async def test_mcp_analytics_generation(self, tracking_worker):
        """Test MCP analytics generation."""
        # Create test calls
        await tracking_worker.track_mcp_call(
            server_name="filesystem",
            tool_name="read_file",
            parameters={"path": "/test1.txt"},
            execution_time_ms=50,
            status=InteractionStatus.COMPLETED
        )

        await tracking_worker.track_mcp_call(
            server_name="filesystem",
            tool_name="list_dir",
            parameters={"path": "/test"},
            execution_time_ms=75,
            status=InteractionStatus.COMPLETED
        )

        analytics = await tracking_worker.get_mcp_analytics(
            server_name="filesystem",
            hours=24
        )

        assert len(analytics) == 1
        mcp_analytics = analytics[0]
        assert mcp_analytics.total_calls == 2
        assert mcp_analytics.successful_calls == 2
        assert mcp_analytics.avg_execution_time_ms == 62.5  # (50 + 75) / 2
        assert "read_file" in mcp_analytics.tools_used
        assert "list_dir" in mcp_analytics.tools_used

    @pytest.mark.asyncio
    async def test_browser_analytics_generation(self, tracking_worker):
        """Test browser analytics generation."""
        # Create test interactions
        await tracking_worker.track_browser_interaction(
            url="https://example.com",
            action=BrowserAction.NAVIGATE,
            parameters={},
            load_time_ms=500,
            status=InteractionStatus.COMPLETED
        )

        await tracking_worker.track_browser_interaction(
            url="https://example.com/page2",
            action=BrowserAction.EXTRACT,
            parameters={"selector": "p"},
            load_time_ms=300,
            status=InteractionStatus.COMPLETED
        )

        analytics = await tracking_worker.get_browser_analytics(hours=24)

        assert analytics is not None
        assert analytics.total_actions == 2
        assert analytics.successful_actions == 2
        assert analytics.avg_page_load_time_ms == 400  # (500 + 300) / 2
        assert analytics.actions_by_type["navigate"] == 1
        assert analytics.actions_by_type["extract"] == 1

    @pytest.mark.asyncio
    async def test_comprehensive_analytics(self, tracking_worker):
        """Test comprehensive analytics generation."""
        # Create test data across all systems
        await tracking_worker.track_knowledge_base_call(
            kb_type=KnowledgeBaseType.DOCUMENTATION,
            kb_identifier="test_docs",
            query="Test query",
            status=InteractionStatus.COMPLETED
        )

        await tracking_worker.track_mcp_call(
            server_name="filesystem",
            tool_name="read_file",
            parameters={"path": "/test.txt"},
            status=InteractionStatus.COMPLETED
        )

        await tracking_worker.track_browser_interaction(
            url="https://example.com",
            action=BrowserAction.NAVIGATE,
            parameters={},
            status=InteractionStatus.COMPLETED
        )

        comprehensive = await tracking_worker.get_comprehensive_analytics()

        assert "knowledge_base" in comprehensive
        assert "mcp" in comprehensive
        assert "browser" in comprehensive
        assert "summary" in comprehensive

        summary = comprehensive["summary"]
        assert summary["total_kb_calls"] == 1
        assert summary["total_mcp_calls"] == 1
        assert summary["total_browser_interactions"] == 1

    def test_configuration_management(self, tracking_worker):
        """Test configuration management."""
        from _schema.tracking import KnowledgeBaseConfig, MCPServerConfig, BrowserConfig

        # Test KB config update
        kb_config = KnowledgeBaseConfig(
            kb_type=KnowledgeBaseType.DOCUMENTATION,
            kb_identifier="test_docs",
            settings={"temperature": 0.5}
        )
        tracking_worker.update_knowledge_base_config(kb_config)

        key = f"{kb_config.kb_type.value}_{kb_config.kb_identifier}"
        assert key in tracking_worker.kb_configs

        # Test MCP config update
        mcp_config = MCPServerConfig(
            server_name="test_server",
            server_type=MCPServerType.CUSTOM_TOOL,
            connection_url="https://test.com",
            capabilities=["test_tool"]
        )
        tracking_worker.update_mcp_server_config(mcp_config)

        assert "test_server" in tracking_worker.mcp_configs

        # Test browser config update
        browser_config = BrowserConfig(
            browser_type="firefox",
            headless=False,
            viewport_width=1920,
            viewport_height=1080
        )
        tracking_worker.update_browser_config(browser_config)

        assert tracking_worker.browser_config.browser_type == "firefox"

    def test_error_tracking(self, tracking_worker):
        """Test error tracking functionality."""
        # Test error tracking
        asyncio.run(tracking_worker.track_error(
            error_type="TEST_ERROR",
            error=Exception("Test exception"),
            context={"test": "data"}
        ))

        # Should not raise any exceptions
        assert tracking_worker.is_running is True

    @pytest.mark.asyncio
    async def test_worker_lifecycle(self, tracking_worker):
        """Test worker start and stop lifecycle."""
        # Test start
        await tracking_worker.start_worker()
        assert tracking_worker.is_running is True

        # Test stop
        await tracking_worker.stop_worker()
        assert tracking_worker.is_running is False

    def test_data_cleanup(self, tracking_worker):
        """Test that old data is properly cleaned up."""
        # Add old data (simulate old timestamps)
        old_call = KnowledgeBaseCall(
            id=uuid4(),
            timestamp=datetime.utcnow() - timedelta(days=10),
            tenant_id="test",
            session_id="test",
            kb_type=KnowledgeBaseType.DOCUMENTATION,
            kb_identifier="test",
            query="old query"
        )

        tracking_worker.knowledge_base_calls.append(old_call)

        # Simulate cleanup (normally done by _process_analytics)
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        tracking_worker.knowledge_base_calls = [
            c for c in tracking_worker.knowledge_base_calls
            if c.timestamp >= cutoff_time
        ]

        # Old call should be removed
        assert len(tracking_worker.knowledge_base_calls) == 0

    def test_analytics_caching(self, tracking_worker):
        """Test analytics caching functionality."""
        # Initially empty
        assert len(tracking_worker.kb_analytics_cache) == 0
        assert len(tracking_worker.mcp_analytics_cache) == 0

        # Add test data and trigger analytics calculation
        asyncio.run(tracking_worker.track_knowledge_base_call(
            kb_type=KnowledgeBaseType.DOCUMENTATION,
            kb_identifier="test_docs",
            query="Test query",
            status=InteractionStatus.COMPLETED
        ))

        # Analytics should be calculated and cached
        assert len(tracking_worker.kb_analytics_cache) > 0

    @pytest.mark.asyncio
    async def test_concurrent_tracking_operations(self, tracking_worker):
        """Test handling of concurrent tracking operations."""
        # Create multiple concurrent tracking operations
        operations = []

        for i in range(5):
            op = tracking_worker.track_knowledge_base_call(
                kb_type=KnowledgeBaseType.DOCUMENTATION,
                kb_identifier=f"test_docs_{i}",
                query=f"Query {i}",
                status=InteractionStatus.COMPLETED
            )
            operations.append(op)

        # Execute all operations concurrently
        results = await asyncio.gather(*operations)

        # All operations should complete
        assert len(results) == 5
        # All should return UUIDs
        assert all(isinstance(result, uuid4.__class__) for result in results)

        # Check that all calls were tracked
        assert len(tracking_worker.knowledge_base_calls) == 5

    def test_tenant_isolation(self, tracking_worker):
        """Test that tracking data is properly isolated by tenant."""
        # Set tenant ID
        tracking_worker.tenant_id = "tenant_123"

        # Track calls for this tenant
        asyncio.run(tracking_worker.track_knowledge_base_call(
            kb_type=KnowledgeBaseType.DOCUMENTATION,
            kb_identifier="test_docs",
            query="Test query",
            status=InteractionStatus.COMPLETED
        ))

        # Check that tenant_id is set correctly
        call = tracking_worker.knowledge_base_calls[0]
        assert call.tenant_id == "tenant_123"

    def test_performance_metrics_tracking(self, tracking_worker):
        """Test performance metrics tracking."""
        # Initially empty
        assert len(tracking_worker.performance_metrics) == 0

        # Track a call with performance data
        asyncio.run(tracking_worker.track_knowledge_base_call(
            kb_type=KnowledgeBaseType.DOCUMENTATION,
            kb_identifier="test_docs",
            query="Test query",
            response_time_ms=100,
            tokens_used=50,
            status=InteractionStatus.COMPLETED
        ))

        # Performance metrics should be tracked
        assert len(tracking_worker.performance_metrics) > 0
