"""
Conversion Worker for advanced conversion tracking and optimization.

This worker implements sophisticated conversion tracking, funnel analysis,
and optimization strategies for bot-facilitated transactions and signups.
"""
from __future__ import annotations

import asyncio
import logging
import json
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, Counter

from app.models import Group, Member
from workers.base_worker import BaseWorker

logger = logging.getLogger(__name__)

@dataclass
class ConversionFunnel:
    """Represents a conversion funnel with stages and tracking."""
    funnel_id: str
    funnel_name: str
    tenant_id: str
    stages: List[str] = field(default_factory=list)
    conversion_goals: Dict[str, str] = field(default_factory=dict)  # stage -> goal

@dataclass
class UserJourney:
    """Tracks a user's journey through conversion funnels."""
    user_id: str
    tenant_id: str
    group_id: str
    journey_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    # Journey tracking
    current_stage: str = "awareness"
    stages_visited: List[Tuple[str, datetime]] = field(default_factory=list)
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)

    # Conversion outcome
    conversion_completed: bool = False
    conversion_value: Optional[float] = None
    conversion_timestamp: Optional[datetime] = None

    # Journey metadata
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

class ConversionWorker(BaseWorker):
    """
    Advanced worker for conversion tracking and optimization.

    Implements comprehensive conversion funnel analysis, A/B testing,
    and optimization strategies for bot-facilitated conversions.
    """

    def __init__(self, groupme_client, db_session):
        super().__init__(groupme_client, db_session)
        self.active_funnels: Dict[str, ConversionFunnel] = {}
        self.user_journeys: Dict[str, UserJourney] = {}
        self.conversion_events: List[Dict[str, Any]] = []
        self.funnel_analytics: Dict[str, Dict[str, Any]] = defaultdict(dict)

        # A/B testing configuration
        self.ab_tests: Dict[str, Dict[str, Any]] = {}
        self.test_results: Dict[str, Dict[str, Any]] = {}

    async def initialize(self) -> None:
        """Initialize the conversion worker."""
        logger.info("Initializing ConversionWorker")

        # Load conversion funnels
        await self._load_conversion_funnels()

        # Initialize journey tracking
        await self._initialize_journey_tracking()

        logger.info("ConversionWorker initialization complete")

    async def _load_conversion_funnels(self) -> None:
        """Load conversion funnel configurations."""
        # Default funnels - in production, load from database
        default_funnels = [
            ConversionFunnel(
                funnel_id="ecommerce_checkout",
                funnel_name="E-commerce Checkout",
                tenant_id="default",
                stages=["awareness", "interest", "consideration", "purchase", "retention"],
                conversion_goals={
                    "purchase": "completed_checkout",
                    "retention": "repeat_purchase"
                }
            ),
            ConversionFunnel(
                funnel_id="subscription_signup",
                funnel_name="Subscription Signup",
                tenant_id="default",
                stages=["awareness", "interest", "trial", "subscription", "retention"],
                conversion_goals={
                    "subscription": "active_subscription",
                    "retention": "renewal"
                }
            )
        ]

        for funnel in default_funnels:
            self.active_funnels[funnel.funnel_id] = funnel

    async def _initialize_journey_tracking(self) -> None:
        """Initialize journey tracking for active users."""
        # Get recent bot interactions to start journey tracking
        recent_interactions = await self._get_recent_interactions(hours=24)

        for interaction in recent_interactions:
            user_id = interaction.get("user_id")
            group_id = interaction.get("group_id")
            tenant_id = interaction.get("tenant_id", "default")

            if user_id and not self._user_has_active_journey(user_id, tenant_id):
                await self._start_user_journey(user_id, group_id, tenant_id)

    def _user_has_active_journey(self, user_id: str, tenant_id: str) -> bool:
        """Check if user has an active journey."""
        return any(
            journey.user_id == user_id and journey.tenant_id == tenant_id
            for journey in self.user_journeys.values()
        )

    async def _start_user_journey(self, user_id: str, group_id: str, tenant_id: str) -> None:
        """Start a new user journey."""
        journey = UserJourney(
            user_id=user_id,
            tenant_id=tenant_id,
            group_id=group_id
        )

        # Determine initial stage based on user message
        initial_stage = await self._determine_initial_stage(user_id, group_id)
        journey.current_stage = initial_stage
        journey.stages_visited.append((initial_stage, datetime.utcnow()))

        self.user_journeys[journey.journey_id] = journey

        logger.info(f"Started journey for user {user_id}: {journey.journey_id}")

    async def _determine_initial_stage(self, user_id: str, group_id: str) -> str:
        """Determine initial funnel stage for a user."""
        # Analyze user message to determine intent and stage
        # For now, use simple keyword matching
        return "awareness"  # Default stage

    async def track_conversion_event(self, event_data: Dict[str, Any]) -> None:
        """Track a conversion-related event."""
        event_type = event_data.get("event_type")
        user_id = event_data.get("user_id")
        group_id = event_data.get("group_id")
        tenant_id = event_data.get("tenant_id", "default")

        if not event_type or not user_id:
            return

        # Log the event
        event_record = {
            "event_type": event_type,
            "user_id": user_id,
            "group_id": group_id,
            "tenant_id": tenant_id,
            "timestamp": datetime.utcnow(),
            "data": event_data
        }

        self.conversion_events.append(event_record)

        # Update user journey if applicable
        await self._update_user_journey(user_id, tenant_id, event_data)

        # Analyze for conversion opportunities
        await self._analyze_conversion_opportunity(event_data)

    async def _update_user_journey(self, user_id: str, tenant_id: str, event_data: Dict[str, Any]) -> None:
        """Update user journey based on conversion event."""
        # Find active journey for this user
        active_journey = None
        for journey in self.user_journeys.values():
            if (journey.user_id == user_id and
                journey.tenant_id == tenant_id and
                not journey.conversion_completed):
                active_journey = journey
                break

        if not active_journey:
            return

        event_type = event_data.get("event_type")

        # Update journey based on event type
        if event_type == "bot_response":
            # User engaged with bot - move to interest stage
            if active_journey.current_stage == "awareness":
                active_journey.current_stage = "interest"
                active_journey.stages_visited.append(("interest", datetime.utcnow()))

        elif event_type == "product_view":
            # User viewed product - move to consideration
            if active_journey.current_stage == "interest":
                active_journey.current_stage = "consideration"
                active_journey.stages_visited.append(("consideration", datetime.utcnow()))

        elif event_type == "checkout_started":
            # User started checkout - close to purchase
            active_journey.current_stage = "purchase"
            active_journey.stages_visited.append(("purchase", datetime.utcnow()))

        elif event_type == "purchase_completed":
            # Conversion completed!
            active_journey.conversion_completed = True
            active_journey.conversion_value = event_data.get("value", 0)
            active_journey.conversion_timestamp = datetime.utcnow()

            # Log successful conversion
            logger.info(f"Conversion completed for user {user_id}: ${active_journey.conversion_value}")

        active_journey.last_updated = datetime.utcnow()

    async def _analyze_conversion_opportunity(self, event_data: Dict[str, Any]) -> None:
        """Analyze event for conversion opportunities and trigger optimizations."""
        event_type = event_data.get("event_type")
        user_id = event_data.get("user_id")
        group_id = event_data.get("group_id")

        # Check for abandonment opportunities
        if event_type == "checkout_abandoned":
            await self._handle_checkout_abandonment(user_id, event_data)

        # Check for upselling opportunities
        elif event_type == "purchase_completed":
            await self._trigger_upsell_opportunity(user_id, event_data)

    async def _handle_checkout_abandonment(self, user_id: str, event_data: Dict[str, Any]) -> None:
        """Handle checkout abandonment with recovery attempts."""
        # Get user's journey
        active_journey = None
        for journey in self.user_journeys.values():
            if journey.user_id == user_id and not journey.conversion_completed:
                active_journey = journey
                break

        if not active_journey:
            return

        # Determine abandonment reason and send recovery message
        abandonment_reason = event_data.get("reason", "unknown")

        if abandonment_reason == "price_too_high":
            recovery_message = (
                "I noticed you were checking out but paused. "
                "We have a special discount available - would you like to apply it?"
            )
        elif abandonment_reason == "payment_issues":
            recovery_message = (
                "Having trouble with payment? "
                "We accept multiple payment methods. Let me help you complete your purchase!"
            )
        else:
            recovery_message = (
                "Almost there! Complete your purchase to get your items. "
                "Need help with anything?"
            )

        try:
            # Send recovery message
            await self.groupme.messages.post_to_group(
                group_id=event_data.get("group_id"),
                source_guid=str(uuid.uuid4()),
                text=recovery_message
            )

            # Log recovery attempt
            logger.info(f"Sent checkout recovery message to user {user_id}")

        except Exception as e:
            logger.error(f"Failed to send recovery message: {e}")

    async def _trigger_upsell_opportunity(self, user_id: str, event_data: Dict[str, Any]) -> None:
        """Trigger upsell opportunity after successful purchase."""
        # Get user's journey
        completed_journey = None
        for journey in self.user_journeys.values():
            if (journey.user_id == user_id and
                journey.conversion_completed and
                journey.conversion_timestamp and
                (datetime.utcnow() - journey.conversion_timestamp) < timedelta(hours=1)):
                completed_journey = journey
                break

        if not completed_journey:
            return

        # Generate upsell message based on purchase
        purchase_category = event_data.get("category", "general")

        if purchase_category == "electronics":
            upsell_message = (
                "Thanks for your purchase! 🎉\n\n"
                "You might also like our premium accessories bundle - "
                "get 20% off when you buy together!"
            )
        elif purchase_category == "clothing":
            upsell_message = (
                "Great choice! 👕\n\n"
                "Complete your look with our matching accessories - "
                "special bundle pricing available!"
            )
        else:
            upsell_message = (
                "Thank you for your purchase! 🌟\n\n"
                "As a valued customer, you qualify for our loyalty program - "
                "earn points on future purchases!"
            )

        try:
            # Send upsell message
            await self.groupme.messages.post_to_group(
                group_id=event_data.get("group_id"),
                source_guid=str(uuid.uuid4()),
                text=upsell_message
            )

            logger.info(f"Sent upsell message to user {user_id}")

        except Exception as e:
            logger.error(f"Failed to send upsell message: {e}")

    async def get_conversion_analytics(self) -> Dict[str, Any]:
        """Get comprehensive conversion analytics."""
        if not self.conversion_events:
            return {"total_events": 0, "message": "No conversion data available"}

        # Aggregate conversion metrics
        total_events = len(self.conversion_events)

        # Event type distribution
        event_types = Counter(event["event_type"] for event in self.conversion_events)

        # Conversion funnel analysis
        funnel_analysis = await self._analyze_conversion_funnels()

        # Journey completion rates
        completed_journeys = len([
            j for j in self.user_journeys.values()
            if j.conversion_completed
        ])
        total_journeys = len(self.user_journeys)

        return {
            "total_conversion_events": total_events,
            "event_type_distribution": dict(event_types),
            "funnel_analysis": funnel_analysis,
            "journey_completion_rate": completed_journeys / total_journeys if total_journeys > 0 else 0,
            "total_revenue_tracked": sum(
                event.get("data", {}).get("value", 0)
                for event in self.conversion_events
                if event.get("event_type") == "purchase_completed"
            ),
            "ab_test_results": self.test_results
        }

    async def _analyze_conversion_funnels(self) -> Dict[str, Any]:
        """Analyze conversion funnel performance."""
        funnel_metrics = {}

        for funnel_id, funnel in self.active_funnels.items():
            # Get journeys for this funnel
            funnel_journeys = [
                j for j in self.user_journeys.values()
                if j.conversion_completed  # Only analyze completed journeys
            ]

            if not funnel_journeys:
                funnel_metrics[funnel_id] = {"conversion_rate": 0, "avg_time_to_convert": 0}
                continue

            # Calculate conversion rate
            conversion_rate = len(funnel_journeys) / len([
                j for j in self.user_journeys.values()
            ]) if self.user_journeys else 0

            # Calculate average time to conversion
            conversion_times = [
                (j.conversion_timestamp - j.started_at).total_seconds()
                for j in funnel_journeys
                if j.conversion_timestamp
            ]

            avg_time = sum(conversion_times) / len(conversion_times) if conversion_times else 0

            funnel_metrics[funnel_id] = {
                "conversion_rate": conversion_rate,
                "avg_time_to_convert_seconds": avg_time,
                "total_conversions": len(funnel_journeys)
            }

        return funnel_metrics

    def setup_ab_test(self, test_config: Dict[str, Any]) -> str:
        """Set up an A/B test for conversion optimization."""
        test_id = str(uuid.uuid4())

        self.ab_tests[test_id] = {
            "test_name": test_config["name"],
            "test_type": test_config["type"],
            "variants": test_config["variants"],
            "target_metric": test_config["target_metric"],
            "start_date": datetime.utcnow(),
            "status": "active"
        }

        logger.info(f"Set up A/B test: {test_config['name']} (ID: {test_id})")
        return test_id

    async def run_ab_test_analysis(self, test_id: str) -> Dict[str, Any]:
        """Analyze results of an A/B test."""
        if test_id not in self.ab_tests:
            return {"error": "Test not found"}

        test_config = self.ab_tests[test_id]

        # Get conversion data for the test period
        test_start = test_config["start_date"]
        test_conversions = [
            event for event in self.conversion_events
            if event["timestamp"] >= test_start
        ]

        # Analyze by variant (simplified - in reality, you'd track which variant each user saw)
        # For now, assume even distribution
        total_conversions = len(test_conversions)
        variants = test_config["variants"]

        if total_conversions == 0:
            return {"status": "insufficient_data"}

        # Simple analysis - in practice, use statistical testing
        variant_results = {}
        for i, variant in enumerate(variants):
            # Simulate variant assignment (every other conversion)
            variant_conversions = total_conversions // len(variants)
            if i < total_conversions % len(variants):
                variant_conversions += 1

            variant_results[variant["name"]] = {
                "conversions": variant_conversions,
                "conversion_rate": variant_conversions / total_conversions
            }

        # Determine winner
        winner = max(variant_results.items(), key=lambda x: x[1]["conversion_rate"])[0]

        self.test_results[test_id] = {
            "test_name": test_config["test_name"],
            "total_conversions": total_conversions,
            "variant_results": variant_results,
            "winner": winner,
            "analysis_timestamp": datetime.utcnow()
        }

        return self.test_results[test_id]

    async def optimize_conversion_strategy(self, funnel_id: str) -> Dict[str, Any]:
        """Generate optimization recommendations for a conversion funnel."""
        funnel = self.active_funnels.get(funnel_id)
        if not funnel:
            return {"error": "Funnel not found"}

        # Analyze drop-off points
        drop_off_analysis = await self._analyze_drop_off_points(funnel_id)

        # Generate recommendations
        recommendations = []

        for stage, drop_off_rate in drop_off_analysis.items():
            if drop_off_rate > 0.3:  # 30% drop-off threshold
                recommendations.append({
                    "stage": stage,
                    "issue": f"High drop-off rate: {drop_off_rate:.1%}",
                    "recommendation": f"Optimize {stage} stage messaging and UX",
                    "priority": "high" if drop_off_rate > 0.5 else "medium"
                })

        return {
            "funnel_id": funnel_id,
            "funnel_name": funnel.funnel_name,
            "drop_off_analysis": drop_off_analysis,
            "recommendations": recommendations,
            "optimization_timestamp": datetime.utcnow()
        }

    async def _analyze_drop_off_points(self, funnel_id: str) -> Dict[str, float]:
        """Analyze where users drop off in the conversion funnel."""
        # Get journeys for this funnel
        funnel_journeys = [
            j for j in self.user_journeys.values()
            if j.conversion_completed  # Only analyze completed journeys
        ]

        if not funnel_journeys:
            return {}

        funnel = self.active_funnels[funnel_id]
        drop_off_rates = {}

        for i, stage in enumerate(funnel.stages[:-1]):  # All stages except last
            next_stage = funnel.stages[i + 1]

            # Count users who reached this stage
            reached_stage = len([
                j for j in funnel_journeys
                if any(s[0] == stage for s in j.stages_visited)
            ])

            # Count users who reached next stage
            reached_next = len([
                j for j in funnel_journeys
                if any(s[0] == next_stage for s in j.stages_visited)
            ])

            if reached_stage > 0:
                drop_off_rate = 1 - (reached_next / reached_stage)
                drop_off_rates[stage] = drop_off_rate

        return drop_off_rates

    async def start_worker(self) -> None:
        """Start the conversion worker."""
        logger.info("Starting ConversionWorker")

        await self.initialize()

        # Start conversion analysis
        asyncio.create_task(self._run_conversion_analysis())

        # Keep worker alive
        while self.is_running:
            await asyncio.sleep(10)

    async def _run_conversion_analysis(self) -> None:
        """Run periodic conversion analysis and optimization."""
        while self.is_running:
            try:
                # Analyze all active funnels
                for funnel_id in self.active_funnels.keys():
                    await self.optimize_conversion_strategy(funnel_id)

                # Clean up old events
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                self.conversion_events = [
                    event for event in self.conversion_events
                    if event["timestamp"] > cutoff_time
                ]

                await asyncio.sleep(3600)  # Run every hour

            except Exception as e:
                logger.error(f"Error in conversion analysis: {e}")
                await asyncio.sleep(3600)

    async def stop_worker(self) -> None:
        """Stop the conversion worker."""
        logger.info("Stopping ConversionWorker")
        self.is_running = False
