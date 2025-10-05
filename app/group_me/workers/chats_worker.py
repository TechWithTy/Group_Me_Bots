"""
Chats Worker for GroupMe chat management and bot operations.

This worker handles:
1. Chat data retrieval and processing
2. Message like/unlike operations
3. Bot lifecycle management (create, list, post, destroy)
4. Integration with existing worker ecosystem
5. Error handling and performance monitoring

Implements comprehensive chat and bot management for the SaaS GroupMe bot platform.
"""
from __future__ import annotations
import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict

from app.models import Group, Member, Chat, Bot
from workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)

@dataclass
class ChatAnalytics:
    """Analytics data for a chat."""
    id: str
    message_count: int
    participant_count: int
    last_activity: datetime
    engagement_score: float
@dataclass
class BotOperation:
    """Represents a bot operation request."""
    operation_type: str  # create, post, destroy, list
    bot_id: Optional[str] = None
    group_id: Optional[str] = None
    message_text: Optional[str] = None
    bot_config: Optional[Dict[str, Any]] = None

@dataclass
class MessageInteraction:
    """Represents a message like/unlike operation."""
    conversation_id: str
    message_id: str
    operation: str  # like, unlike
    user_id: str
    timestamp: datetime

class ChatsWorker(BaseWorker):
    """
    Advanced worker for GroupMe chat management and bot operations.

    Handles chat data processing, message interactions, bot lifecycle management,
    and integrates with analytics and engagement systems.
    """

    def __init__(self, groupme_client, db_session):
        super().__init__(groupme_client, db_session)

        # Chat and bot management
        self.chat_cache: Dict[str, Dict[str, Any]] = {}
        self.bot_cache: Dict[str, Dict[str, Any]] = {}
        self.message_interactions: List[MessageInteraction] = []

        # Operation queues
        self.bot_operation_queue: asyncio.Queue = asyncio.Queue()
        self.message_operation_queue: asyncio.Queue = asyncio.Queue()

        # Analytics tracking
        self.chat_analytics: Dict[str, ChatAnalytics] = {}
        self.bot_performance: Dict[str, Dict[str, Any]] = defaultdict(dict)

    async def initialize(self) -> None:
        """Initialize the chats worker."""
        logger.info("Initializing ChatsWorker")

        # Load existing chats and bots for this tenant
        await self._load_tenant_chats_and_bots()

        # Start operation processors
        asyncio.create_task(self._process_bot_operations())
        asyncio.create_task(self._process_message_operations())

        logger.info("ChatsWorker initialization complete")

    async def _load_tenant_chats_and_bots(self) -> None:
        """Load existing chats and bots for the current tenant."""
        try:
            # Load chats (mock implementation)
            chats_data = await self._get_tenant_chats()
            for chat_data in chats_data:
                self.chat_cache[chat_data["id"]] = chat_data

            # Load bots (mock implementation)
            bots_data = await self._get_tenant_bots()
            for bot_data in bots_data:
                self.bot_cache[bot_data["bot_id"]] = bot_data

            logger.info(f"Loaded {len(chats_data)} chats and {len(bots_data)} bots for tenant")

        except Exception as e:
            logger.error(f"Error loading tenant chats and bots: {e}")

    # Chat Management Operations

    async def get_chats_paginated(self, page: int = 1, per_page: int = 20) -> List[Dict[str, Any]]:
        """Get paginated list of chats for the current tenant."""
        try:
            # In production, this would call the actual GroupMe API
            # For now, return cached or mock data
            all_chats = list(self.chat_cache.values())

            # Simple pagination
            start_index = (page - 1) * per_page
            end_index = start_index + per_page

            return all_chats[start_index:end_index]

        except Exception as e:
            logger.error(f"Error getting chats: {e}")
            return []

    async def refresh_chat_data(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Refresh data for a specific chat."""
        try:
            # In production, call GroupMe API to get latest chat data
            # For now, simulate refresh
            if chat_id in self.chat_cache:
                chat_data = self.chat_cache[chat_id].copy()
                chat_data["updated_at"] = int(datetime.utcnow().timestamp())
                self.chat_cache[chat_id] = chat_data
                return chat_data

            return None

        except Exception as e:
            logger.error(f"Error refreshing chat {chat_id}: {e}")
            return None

    async def get_chat_analytics(self, chat_id: str) -> Optional[ChatAnalytics]:
        """Get analytics for a specific chat."""
        if chat_id not in self.chat_analytics:
            await self._calculate_chat_analytics(chat_id)

        return self.chat_analytics.get(chat_id)

    async def _calculate_chat_analytics(self, chat_id: str) -> None:
        """Calculate analytics for a chat."""
        chat_data = self.chat_cache.get(chat_id)
        if not chat_data:
            return

        # Calculate engagement score based on message frequency and activity
        messages_count = chat_data.get("messages_count", 0)
        days_since_creation = (datetime.utcnow() - datetime.fromtimestamp(chat_data.get("created_at", 0))).days

        if days_since_creation > 0:
            daily_message_rate = messages_count / days_since_creation
            engagement_score = min(daily_message_rate / 10, 1.0)  # Normalize to 0-1 scale
        else:
            engagement_score = 0.0

        analytics = ChatAnalytics(
            chat_id=chat_id,
            tenant_id=self.tenant_id,
            message_count=messages_count,
            participant_count=len(chat_data.get("participants", [])),
            last_activity=datetime.fromtimestamp(chat_data.get("updated_at", 0)),
            engagement_score=engagement_score
        )

        self.chat_analytics[chat_id] = analytics

    # Message Interaction Operations

    async def like_message_async(self, conversation_id: str, message_id: str) -> bool:
        """Like a message asynchronously."""
        try:
            operation = MessageInteraction(
                conversation_id=conversation_id,
                message_id=message_id,
                operation="like",
                user_id=self.tenant_id,  # Using tenant_id as user_id for now
                timestamp=datetime.utcnow()
            )

            await self.message_operation_queue.put(operation)
            return True

        except Exception as e:
            logger.error(f"Error queuing like operation: {e}")
            return False

    async def unlike_message_async(self, conversation_id: str, message_id: str) -> bool:
        """Unlike a message asynchronously."""
        try:
            operation = MessageInteraction(
                conversation_id=conversation_id,
                message_id=message_id,
                operation="unlike",
                user_id=self.tenant_id,
                timestamp=datetime.utcnow()
            )

            await self.message_operation_queue.put(operation)
            return True

        except Exception as e:
            logger.error(f"Error queuing unlike operation: {e}")
            return False

    # Bot Management Operations

    async def create_bot_async(self, name: str, group_id: str, **bot_config) -> Optional[str]:
        """Create a bot asynchronously."""
        try:
            operation = BotOperation(
                operation_type="create",
                bot_config={
                    "name": name,
                    "group_id": group_id,
                    **bot_config
                }
            )

            await self.bot_operation_queue.put(operation)

            # Generate a mock bot_id for immediate response
            bot_id = f"bot_{uuid.uuid4().hex[:8]}"

            # Cache the bot configuration
            self.bot_cache[bot_id] = {
                "bot_id": bot_id,
                "name": name,
                "group_id": group_id,
                "status": "creating",
                **bot_config
            }

            return bot_id

        except Exception as e:
            logger.error(f"Error creating bot: {e}")
            return None

    async def post_bot_message_async(self, bot_id: str, text: str, **message_config) -> bool:
        """Post a message from a bot asynchronously."""
        try:
            operation = BotOperation(
                operation_type="post",
                bot_id=bot_id,
                message_text=text,
                **message_config
            )

            await self.bot_operation_queue.put(operation)
            return True

        except Exception as e:
            logger.error(f"Error posting bot message: {e}")
            return False

    async def destroy_bot_async(self, bot_id: str) -> bool:
        """Destroy a bot asynchronously."""
        try:
            operation = BotOperation(
                operation_type="destroy",
                bot_id=bot_id
            )

            await self.bot_operation_queue.put(operation)
            return True

        except Exception as e:
            logger.error(f"Error destroying bot: {e}")
            return False

    async def list_bots_async(self) -> List[Dict[str, Any]]:
        """List bots asynchronously."""
        try:
            operation = BotOperation(operation_type="list")
            await self.bot_operation_queue.put(operation)

            # Return cached bots for immediate response
            return list(self.bot_cache.values())

        except Exception as e:
            logger.error(f"Error listing bots: {e}")
            return []

    # Background Operation Processors

    async def _process_bot_operations(self) -> None:
        """Process bot operation queue."""
        while self.is_running:
            try:
                if not self.bot_operation_queue.empty():
                    operation: BotOperation = await self.bot_operation_queue.get()

                    if operation.operation_type == "create":
                        await self._execute_bot_creation(operation)
                    elif operation.operation_type == "post":
                        await self._execute_bot_message_post(operation)
                    elif operation.operation_type == "destroy":
                        await self._execute_bot_destruction(operation)
                    elif operation.operation_type == "list":
                        await self._execute_bot_listing(operation)

                    await asyncio.sleep(0.1)  # Rate limiting

                else:
                    await asyncio.sleep(1)  # Wait before checking again

            except Exception as e:
                logger.error(f"Error in bot operations processing: {e}")
                await asyncio.sleep(1)

    async def _process_message_operations(self) -> None:
        """Process message operation queue."""
        while self.is_running:
            try:
                if not self.message_operation_queue.empty():
                    operation: MessageInteraction = await self.message_operation_queue.get()

                    if operation.operation == "like":
                        await self._execute_message_like(operation)
                    elif operation.operation == "unlike":
                        await self._execute_message_unlike(operation)

                    await asyncio.sleep(0.1)  # Rate limiting

                else:
                    await asyncio.sleep(1)  # Wait before checking again

            except Exception as e:
                logger.error(f"Error in message operations processing: {e}")
                await asyncio.sleep(1)

    # Operation Execution Methods

    async def _execute_bot_creation(self, operation: BotOperation) -> None:
        """Execute bot creation."""
        try:
            bot_config = operation.bot_config
            bot_id = f"bot_{uuid.uuid4().hex[:8]}"

            # In production, call GroupMe API
            # For now, simulate successful creation
            await asyncio.sleep(0.2)  # Simulate API call

            # Update bot cache
            bot_data = {
                "bot_id": bot_id,
                "group_id": bot_config["group_id"],
                "name": bot_config["name"],
                "avatar_url": bot_config.get("avatar_url"),
                "callback_url": bot_config.get("callback_url"),
                "dm_notification": bot_config.get("dm_notification", False),
                "active": bot_config.get("active", True),
                "status": "active",
                "created_at": int(datetime.utcnow().timestamp())
            }

            self.bot_cache[bot_id] = bot_data

            logger.info(f"Created bot {bot_id}: {bot_data['name']}")

        except Exception as e:
            logger.error(f"Failed to create bot: {e}")

    async def _execute_bot_message_post(self, operation: BotOperation) -> None:
        """Execute bot message posting."""
        try:
            bot_id = operation.bot_id
            text = operation.message_text

            if bot_id not in self.bot_cache:
                logger.error(f"Bot {bot_id} not found")
                return

            bot_data = self.bot_cache[bot_id]

            # In production, call GroupMe API
            # For now, simulate successful posting
            await asyncio.sleep(0.1)  # Simulate API call

            # Update bot performance metrics
            self.bot_performance[bot_id]["messages_sent"] = self.bot_performance[bot_id].get("messages_sent", 0) + 1
            self.bot_performance[bot_id]["last_message_at"] = datetime.utcnow()

            logger.info(f"Posted message from bot {bot_id}: {text[:50]}...")

        except Exception as e:
            logger.error(f"Failed to post bot message: {e}")

    async def _execute_bot_destruction(self, operation: BotOperation) -> None:
        """Execute bot destruction."""
        try:
            bot_id = operation.bot_id

            if bot_id not in self.bot_cache:
                logger.error(f"Bot {bot_id} not found")
                return

            # In production, call GroupMe API
            # For now, simulate successful destruction
            await asyncio.sleep(0.1)  # Simulate API call

            # Remove from cache
            bot_data = self.bot_cache.pop(bot_id)
            self.bot_performance.pop(bot_id, None)

            logger.info(f"Destroyed bot {bot_id}: {bot_data['name']}")

        except Exception as e:
            logger.error(f"Failed to destroy bot: {e}")

    async def _execute_bot_listing(self, operation: BotOperation) -> None:
        """Execute bot listing (refresh cache)."""
        try:
            # In production, call GroupMe API to refresh bot list
            # For now, simulate refresh
            await asyncio.sleep(0.1)  # Simulate API call

            logger.debug("Refreshed bot list from GroupMe API")

        except Exception as e:
            logger.error(f"Failed to list bots: {e}")

    async def _execute_message_like(self, operation: MessageInteraction) -> None:
        """Execute message like operation."""
        try:
            # In production, call GroupMe API
            # For now, simulate successful like
            await asyncio.sleep(0.05)  # Simulate API call

            # Track the interaction
            self.message_interactions.append(operation)

            logger.debug(f"Liked message {operation.message_id} in conversation {operation.conversation_id}")

        except Exception as e:
            logger.error(f"Failed to like message: {e}")

    async def _execute_message_unlike(self, operation: MessageInteraction) -> None:
        """Execute message unlike operation."""
        try:
            # In production, call GroupMe API
            # For now, simulate successful unlike
            await asyncio.sleep(0.05)  # Simulate API call

            # Track the interaction
            self.message_interactions.append(operation)

            logger.debug(f"Unliked message {operation.message_id} in conversation {operation.conversation_id}")

        except Exception as e:
            logger.error(f"Failed to unlike message: {e}")

    # Analytics and Monitoring

    async def get_chat_analytics_summary(self) -> Dict[str, Any]:
        """Get analytics summary for all chats."""
        if not self.chat_analytics:
            return {"total_chats": 0, "message": "No analytics data available"}

        total_chats = len(self.chat_analytics)
        total_messages = sum(analytics.message_count for analytics in self.chat_analytics.values())
        avg_engagement = sum(analytics.engagement_score for analytics in self.chat_analytics.values()) / total_chats

        return {
            "total_chats": total_chats,
            "total_messages": total_messages,
            "average_engagement_score": avg_engagement,
            "most_active_chat": max(
                self.chat_analytics.items(),
                key=lambda x: x[1].engagement_score
            )[0] if self.chat_analytics else None
        }

    async def get_bot_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all bots."""
        if not self.bot_performance:
            return {"total_bots": 0, "message": "No bot performance data available"}

        total_bots = len(self.bot_performance)
        total_messages_sent = sum(perf.get("messages_sent", 0) for perf in self.bot_performance.values())

        return {
            "total_bots": total_bots,
            "total_messages_sent": total_messages_sent,
            "average_messages_per_bot": total_messages_sent / total_bots if total_bots > 0 else 0,
            "bot_performance": dict(self.bot_performance)
        }

    async def get_message_interaction_summary(self) -> Dict[str, Any]:
        """Get summary of message interactions."""
        if not self.message_interactions:
            return {"total_interactions": 0, "message": "No interaction data available"}

        total_interactions = len(self.message_interactions)

        # Count by operation type
        operation_counts = {}
        for interaction in self.message_interactions:
            operation_counts[interaction.operation] = operation_counts.get(interaction.operation, 0) + 1

        return {
            "total_interactions": total_interactions,
            "operation_breakdown": operation_counts,
            "recent_interactions": len([
                i for i in self.message_interactions
                if (datetime.utcnow() - i.timestamp) < timedelta(hours=24)
            ])
        }

    # Integration Methods

    async def _get_tenant_chats(self) -> List[Dict[str, Any]]:
        """Get chats for the current tenant (mock implementation)."""
        # In production, this would query the GroupMe API
        # For now, return cached data
        return list(self.chat_cache.values())

    async def _get_tenant_bots(self) -> List[Dict[str, Any]]:
        """Get bots for the current tenant (mock implementation)."""
        # In production, this would query the GroupMe API
        # For now, return cached data
        return list(self.bot_cache.values())

    async def start_worker(self) -> None:
        """Start the chats worker."""
        logger.info("Starting ChatsWorker")

        await self.initialize()

        # Start periodic analytics updates
        asyncio.create_task(self._run_periodic_analytics())

        # Keep worker alive
        while self.is_running:
            await asyncio.sleep(10)

    async def _run_periodic_analytics(self) -> None:
        """Run periodic analytics updates."""
        while self.is_running:
            try:
                # Update chat analytics
                for chat_id in list(self.chat_cache.keys()):
                    await self._calculate_chat_analytics(chat_id)

                # Update bot performance metrics
                await self._update_bot_performance_metrics()

                # Clean up old interaction data
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                self.message_interactions = [
                    interaction for interaction in self.message_interactions
                    if interaction.timestamp > cutoff_time
                ]

                await asyncio.sleep(3600)  # Run every hour

            except Exception as e:
                logger.error(f"Error in periodic analytics: {e}")
                await asyncio.sleep(3600)

    async def _update_bot_performance_metrics(self) -> None:
        """Update bot performance metrics."""
        for bot_id, bot_data in self.bot_cache.items():
            # Calculate performance metrics
            messages_sent = self.bot_performance[bot_id].get("messages_sent", 0)
            last_message_at = self.bot_performance[bot_id].get("last_message_at")

            if last_message_at:
                hours_since_last_message = (datetime.utcnow() - last_message_at).total_seconds() / 3600
                activity_score = min(messages_sent / max(hours_since_last_message, 1), 10.0)
            else:
                activity_score = 0.0

            self.bot_performance[bot_id].update({
                "activity_score": activity_score,
                "total_messages": messages_sent,
                "last_updated": datetime.utcnow()
            })

    async def stop_worker(self) -> None:
        """Stop the chats worker."""
        logger.info("Stopping ChatsWorker")

        # Cancel background tasks
        if hasattr(self.bot_operation_queue, 'task'):
            self.bot_operation_queue.task.cancel()

        if hasattr(self.message_operation_queue, 'task'):
            self.message_operation_queue.task.cancel()

        self.is_running = False

        logger.info("ChatsWorker stopped")
