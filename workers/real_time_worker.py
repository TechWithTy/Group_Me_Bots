"""
Real-time worker for GroupMe push subscriptions and live event handling.

This worker implements GroupMe's Faye/push protocol for real-time message detection,
enabling instant responses, live engagement tracking, and advanced automation features.
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import aiohttp
import websockets
from websockets.exceptions import ConnectionClosed

from app.models import Group, Member
from workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)

@dataclass
class PushSubscription:
    """Represents a GroupMe push subscription."""
    group_id: str
    client_id: str
    subscription_channel: str
    last_activity: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True

@dataclass
class RealTimeEvent:
    """Represents a real-time event from GroupMe push."""
    event_type: str  # "message", "member_joined", "member_left", etc.
    group_id: str
    timestamp: datetime
    data: Dict[str, Any]
    source: str = "push"

class RealTimeWorker(BaseWorker):
    """
    Advanced worker for real-time GroupMe push subscriptions.

    Implements GroupMe's Faye/push protocol for instant message detection and response.
    Supports multiple subscription channels and real-time event processing.
    """

    def __init__(self, groupme_client, db_session):
        super().__init__(groupme_client, db_session)
        self.subscriptions: Dict[str, PushSubscription] = {}
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.websocket_connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.heartbeat_interval = 30  # seconds

        # Faye/push server configuration
        self.faye_server = "https://push.groupme.com"
        self.faye_client_endpoint = "/faye"

    async def initialize(self) -> None:
        """Initialize the real-time worker and establish subscriptions."""
        logger.info("Initializing RealTimeWorker")

        # Get all active groups for this tenant
        groups = await self.get_active_groups()
        logger.info(f"Found {len(groups)} active groups to monitor")

        # Establish subscriptions for each group
        for group in groups:
            await self.subscribe_to_group(group.id)

        logger.info("RealTimeWorker initialization complete")

    async def subscribe_to_group(self, group_id: str) -> None:
        """Establish a real-time subscription to a GroupMe group."""
        try:
            # Step 1: Handshake to get client_id
            client_id = await self._perform_handshake()

            # Step 2: Subscribe to group channel
            subscription_channel = f"/group/{group_id}"

            subscription = PushSubscription(
                group_id=group_id,
                client_id=client_id,
                subscription_channel=subscription_channel
            )

            self.subscriptions[group_id] = subscription

            # Step 3: Start listening for events
            asyncio.create_task(self._listen_for_events(subscription))

            logger.info(f"Subscribed to real-time events for group {group_id}")

        except Exception as e:
            logger.error(f"Failed to subscribe to group {group_id}: {e}")

    async def _perform_handshake(self) -> str:
        """Perform Faye handshake to get client_id."""
        handshake_data = {
            "channel": "/meta/handshake",
            "version": "1.0",
            "supportedConnectionTypes": ["websocket", "long-polling"]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.faye_server}{self.faye_client_endpoint}",
                json=[handshake_data],
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    raise Exception(f"Handshake failed: {response.status}")

                handshake_response = await response.json()
                client_id = handshake_response[0]["clientId"]

                logger.debug(f"Handshake successful, client_id: {client_id}")
                return client_id

    async def _listen_for_events(self, subscription: PushSubscription) -> None:
        """Listen for real-time events on a subscription."""
        while subscription.is_active:
            try:
                # Use long-polling for simplicity (can be upgraded to WebSocket)
                events = await self._long_poll_for_events(subscription)

                for event_data in events:
                    event = RealTimeEvent(
                        event_type=event_data.get("data", {}).get("type", "unknown"),
                        group_id=subscription.group_id,
                        timestamp=datetime.utcnow(),
                        data=event_data
                    )

                    # Process the event
                    await self._process_real_time_event(event)

                    # Update subscription activity
                    subscription.last_activity = datetime.utcnow()

            except Exception as e:
                logger.error(f"Error in event listener for {subscription.group_id}: {e}")
                await asyncio.sleep(5)  # Back off before retrying

    async def _long_poll_for_events(self, subscription: PushSubscription) -> List[Dict]:
        """Perform long-polling for events on a subscription."""
        poll_data = [{
            "channel": subscription.subscription_channel,
            "clientId": subscription.client_id,
            "id": str(int(time.time() * 1000))
        }]

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.faye_server}{self.faye_client_endpoint}",
                json=poll_data,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return [item for item in response_data if item.get("channel") == subscription.subscription_channel]
                else:
                    logger.warning(f"Long poll failed for {subscription.group_id}: {response.status}")
                    return []

    async def _process_real_time_event(self, event: RealTimeEvent) -> None:
        """Process a real-time event and trigger appropriate handlers."""
        logger.debug(f"Processing real-time event: {event.event_type} in group {event.group_id}")

        # Trigger event handlers
        if event.event_type in self.event_handlers:
            for handler in self.event_handlers[event.event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error in event handler for {event.event_type}: {e}")

        # Default event processing
        if event.event_type == "message":
            await self._handle_real_time_message(event)
        elif event.event_type == "member_joined":
            await self._handle_member_joined(event)
        elif event.event_type == "member_left":
            await self._handle_member_left(event)

    async def _handle_real_time_message(self, event: RealTimeEvent) -> None:
        """Handle real-time message events with instant response capability."""
        message_data = event.data.get("data", {})
        message_text = message_data.get("text", "")
        user_id = message_data.get("user_id")

        if not message_text or not user_id:
            return

        # Check for trigger keywords that need instant response
        if await self._should_respond_instantly(message_text, event.group_id):
            # Generate instant response
            response_text = await self._generate_instant_response(message_text, event.group_id)

            if response_text:
                # Send response immediately
                await self.groupme.messages.post_to_group(
                    group_id=event.group_id,
                    source_guid=str(uuid.uuid4()),
                    text=response_text
                )

                logger.info(f"Sent instant response to group {event.group_id}")

    async def _handle_member_joined(self, event: RealTimeEvent) -> None:
        """Handle real-time member joined events."""
        member_data = event.data.get("data", {})
        user_id = member_data.get("user_id")

        if user_id:
            # Trigger welcome sequence immediately
            await self._trigger_instant_welcome(user_id, event.group_id)

    async def _handle_member_left(self, event: RealTimeEvent) -> None:
        """Handle real-time member left events."""
        member_data = event.data.get("data", {})
        user_id = member_data.get("user_id")

        if user_id:
            # Track churn and potentially trigger retention efforts
            await self._track_member_churn(user_id, event.group_id)

    async def _should_respond_instantly(self, message_text: str, group_id: str) -> bool:
        """Determine if a message requires instant response."""
        # Check for specific trigger keywords
        instant_triggers = [
            "help", "support", "urgent", "asap",
            "buy", "purchase", "price", "cost",
            "join", "invite", "add me"
        ]

        message_lower = message_text.lower()
        return any(trigger in message_lower for trigger in instant_triggers)

    async def _generate_instant_response(self, message_text: str, group_id: str) -> Optional[str]:
        """Generate an instant response to a trigger message."""
        # Simple keyword-based responses (can be enhanced with AI)
        responses = {
            "help": "I can help you! What do you need assistance with?",
            "buy": "Looking to purchase? I can help with recommendations and deals!",
            "join": "Want to join our community? Send me a DM for an invite!",
            "urgent": "I understand this is urgent. Let me assist you right away."
        }

        message_lower = message_text.lower()
        for keyword, response in responses.items():
            if keyword in message_lower:
                return response

        return None

    async def _trigger_instant_welcome(self, user_id: str, group_id: str) -> None:
        """Trigger instant welcome sequence for new members."""
        welcome_message = (
            "Welcome to our community! 🎉\n\n"
            "I'm here to help with:\n"
            "• Product recommendations\n"
            "• Exclusive deals\n"
            "• Community discussions\n\n"
            "Just mention me or ask a question!"
        )

        try:
            await self.groupme.messages.post_to_group(
                group_id=group_id,
                source_guid=str(uuid.uuid4()),
                text=welcome_message
            )
        except Exception as e:
            logger.error(f"Failed to send welcome message: {e}")

    async def _track_member_churn(self, user_id: str, group_id: str) -> None:
        """Track member churn for analytics."""
        # Log churn event for later analysis
        logger.info(f"Member {user_id} left group {group_id}")

        # Could trigger retention campaigns or analytics updates
        # For now, just log the event

    def register_event_handler(self, event_type: str, handler: Callable) -> None:
        """Register a custom event handler."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []

        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for event type: {event_type}")

    async def unsubscribe_from_group(self, group_id: str) -> None:
        """Unsubscribe from real-time events for a group."""
        if group_id in self.subscriptions:
            self.subscriptions[group_id].is_active = False
            del self.subscriptions[group_id]
            logger.info(f"Unsubscribed from group {group_id}")

    async def get_subscription_status(self) -> Dict[str, Any]:
        """Get status of all active subscriptions."""
        return {
            "total_subscriptions": len(self.subscriptions),
            "active_subscriptions": len([s for s in self.subscriptions.values() if s.is_active]),
            "subscription_details": {
                group_id: {
                    "client_id": sub.client_id,
                    "last_activity": sub.last_activity.isoformat(),
                    "is_active": sub.is_active
                }
                for group_id, sub in self.subscriptions.items()
            }
        }

    async def run_heartbeat(self) -> None:
        """Run periodic heartbeat to maintain subscriptions."""
        while True:
            try:
                # Check subscription health
                for subscription in self.subscriptions.values():
                    if subscription.is_active:
                        time_since_activity = datetime.utcnow() - subscription.last_activity
                        if time_since_activity > timedelta(minutes=5):
                            logger.warning(f"Subscription {subscription.group_id} may be stale")

                await asyncio.sleep(self.heartbeat_interval)

            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                await asyncio.sleep(self.heartbeat_interval)

    async def start_worker(self) -> None:
        """Start the real-time worker."""
        logger.info("Starting RealTimeWorker")

        # Initialize subscriptions
        await self.initialize()

        # Start heartbeat task
        asyncio.create_task(self.run_heartbeat())

        # Keep worker alive
        while self.is_running:
            await asyncio.sleep(10)

    async def stop_worker(self) -> None:
        """Stop the real-time worker and clean up subscriptions."""
        logger.info("Stopping RealTimeWorker")

        # Mark all subscriptions as inactive
        for subscription in self.subscriptions.values():
            subscription.is_active = False

        self.subscriptions.clear()
        self.is_running = False

        logger.info("RealTimeWorker stopped")
